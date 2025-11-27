from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, View
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError

from products.models import Product, Brand
from geo.models import UserProfile, Country
import tablib


class ProductCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        brand_qs = Brand.objects.all()
        if country:
            brand_qs = brand_qs.filter(country=country)
        context['brands'] = brand_qs
        return context


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        brand_qs = Brand.objects.all()
        if country:
            brand_qs = brand_qs.filter(country=country)
        context['brands'] = brand_qs
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['sku', 'description', 'brand']
    template_name = 'products/update.html'
    success_url = reverse_lazy('inventory_control:inventory-control-list')
    # success_message

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        qs = Product.objects.all()
        if country:
            qs = qs.filter(country=country)
        return qs


class ProductBulkUploadView(LoginRequiredMixin, View):
    template_name = 'products/bulk_upload.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        user_country = getattr(profile, 'country', None)
        create_brands = request.POST.get('create_brands', 'off') == 'on'

        try:
            upload_file = request.FILES['file']
        except MultiValueDictKeyError:
            messages.error(request, 'Debe seleccionar un archivo.')
            return render(request, self.template_name)

        # Detect format by extension
        filename = upload_file.name.lower()
        if filename.endswith('.xlsx'):
            file_format = 'xlsx'
            data = upload_file.read()
            dataset = tablib.Dataset().load(data, format=file_format)
        elif filename.endswith('.csv'):
            file_format = 'csv'
            data = upload_file.read().decode('utf-8')
            dataset = tablib.Dataset().load(data, format=file_format)
        else:
            messages.error(request, 'Formato no soportado. Use CSV o Excel (.xlsx).')
            return render(request, self.template_name)

        required_headers = ['sku', 'description', 'brand', 'country']
        # Normalize headers (lowercase)
        header_map = {h.lower(): idx for idx, h in enumerate(dataset.headers or [])}
        missing = [h for h in required_headers if h not in header_map]
        if missing:
            messages.error(request, f'Faltan columnas requeridas: {", ".join(missing)}')
            return render(request, self.template_name)

        created_count = 0
        updated_count = 0
        errors = []
        new_products = []

        for i, row in enumerate(dataset, start=2):  # start=2 to account for header row as 1
            try:
                sku = str(row[header_map['sku']]).strip()
                description = str(row[header_map['description']]).strip()
                brand_name = str(row[header_map['brand']]).strip()
                country_code = str(row[header_map['country']]).strip().upper()

                if not sku:
                    errors.append(f'Fila {i}: SKU vacío')
                    continue

                # Country lookup
                try:
                    country = Country.objects.get(code__iexact=country_code)
                except Country.DoesNotExist:
                    errors.append(f'Fila {i}: País no encontrado para código "{country_code}"')
                    continue

                # Permission: user may only upload for own country
                if user_country and country != user_country:
                    errors.append(f'Fila {i}: País del registro ({country_code}) no coincide con el país del usuario')
                    continue

                # Brand resolve or create
                brand = None
                if brand_name:
                    brand = Brand.objects.filter(name__iexact=brand_name, country=country).first()
                    if not brand:
                        if create_brands:
                            brand = Brand.objects.create(name=brand_name, country=country)
                        else:
                            errors.append(f'Fila {i}: Marca "{brand_name}" no existe en {country.code}')
                            continue

                # Upsert product by (sku, country)
                product = Product.objects.filter(sku=sku, country=country).first()
                if product:
                    changed = False
                    if product.description != description:
                        product.description = description
                        changed = True
                    if brand and product.brand_id != (brand.id if brand else None):
                        product.brand = brand
                        changed = True
                    if changed:
                        product.save()
                        updated_count += 1
                    else:
                        # No change but counts not incremented
                        pass
                else:
                    # Product.objects.create(
                    #     sku=sku,
                    #     description=description,
                    #     brand=brand,
                    #     country=country,
                    # )
                    new_products.append(Product(
                        sku=sku,
                        description=description,
                        brand=brand,
                        country=country
                    ))
                    # created_count += 1
                    
        

            except Exception as ex:
                errors.append(f'Fila {i}: Error inesperado - {ex}')
                
        Product.objects.bulk_create(new_products, batch_size=500)
        created_count = len(new_products)

        context = {
            'created_count': created_count,
            'updated_count': updated_count,
            'errors': errors,
        }
        if errors:
            messages.warning(request, f'Procesado con errores: {len(errors)} problema(s).')
        else:
            messages.success(request, 'Carga procesada correctamente.')
        return render(request, self.template_name, context)


class ProductExportView(LoginRequiredMixin, View):
    """
    Exporta el listado de productos del país del usuario.
    Soporta formatos: xlsx (por defecto) y csv via ?format=
    Filtros opcionales por query: brand (id)
    Columnas: SKU, Descripción, Marca
    """
    def get(self, request):
        export_format = request.GET.get('format', 'xlsx').lower()
        if export_format not in ('xlsx', 'csv'):
            export_format = 'xlsx'

        profile = getattr(request.user, 'profile', None)
        country = getattr(profile, 'country', None)

        qs = Product.objects.select_related('brand').all()
        if country:
            qs = qs.filter(country=country)

        brand_id = request.GET.get('brand')
        if brand_id:
            qs = qs.filter(brand_id=brand_id)

        dataset = tablib.Dataset(headers=['SKU', 'Descripción', 'Marca', 'País'])
        for p in qs.order_by('id'):
            dataset.append([p.sku, p.description or '', p.brand.name if p.brand_id else '', p.country.code if p.country else ''])

        today = datetime.now().strftime('%Y%m%d')
        filename = f'productos_{today}.{"csv" if export_format == "csv" else "xlsx"}'

        if export_format == 'csv':
            content = dataset.export('csv')
            content_type = 'text/csv; charset=utf-8'
        else:
            content = dataset.export('xlsx')
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response