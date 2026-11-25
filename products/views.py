from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, View
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from openpyxl import load_workbook
import csv
import io

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

        filename = upload_file.name.lower()
        if filename.endswith('.xlsx'):
            workbook = load_workbook(upload_file.file, read_only=True, data_only=True)
            worksheet = workbook.active
            rows = worksheet.iter_rows(values_only=True)
            raw_headers = next(rows, None)
            if raw_headers is None:
                messages.error(request, 'El archivo está vacío.')
                workbook.close()
                return render(request, self.template_name)
        elif filename.endswith('.csv'):
            data = upload_file.read().decode('utf-8-sig')
            csv_rows = csv.reader(io.StringIO(data))
            raw_headers = next(csv_rows, None)
            if raw_headers is None:
                messages.error(request, 'El archivo está vacío.')
                return render(request, self.template_name)
        else:
            messages.error(request, 'Formato no soportado. Use CSV o Excel (.xlsx).')
            return render(request, self.template_name)

        required_headers = ['sku', 'description', 'brand', 'country']
        header_map = {
            str(header).strip().lower(): idx
            for idx, header in enumerate(raw_headers)
            if header is not None
        }
        missing = [h for h in required_headers if h not in header_map]
        if missing:
            if filename.endswith('.xlsx'):
                workbook.close()
            messages.error(request, f'Faltan columnas requeridas: {", ".join(missing)}')
            return render(request, self.template_name)

        created_count = 0
        updated_count = 0
        errors = []
        countries = {country.code.upper(): country for country in Country.objects.all()}
        brands = {
            (brand.country_id, brand.name.casefold()): brand
            for brand in Brand.objects.select_related('country').all()
        }
        records = []

        data_rows = rows if filename.endswith('.xlsx') else csv_rows
        for i, row in enumerate(data_rows, start=2):
            try:
                def value(header):
                    idx = header_map[header]
                    return '' if idx >= len(row) or row[idx] is None else str(row[idx]).strip()

                sku = value('sku')
                description = value('description')
                brand_name = value('brand')
                country_code = value('country').upper()

                if not sku:
                    errors.append(f'Fila {i}: SKU vacío')
                    continue

                country = countries.get(country_code)
                if country is None:
                    errors.append(f'Fila {i}: País no encontrado para código "{country_code}"')
                    continue

                if user_country and country != user_country:
                    errors.append(
                        f'Fila {i}: País del registro ({country_code}) no coincide '
                        f'con el país del usuario ({user_country.code}).'
                    )
                    continue

                records.append((i, sku, description, brand_name, country))
            except Exception as ex:
                errors.append(f'Fila {i}: Error inesperado - {ex}')

        if filename.endswith('.xlsx'):
            workbook.close()

        if not records:
            context = {'created_count': 0, 'updated_count': 0, 'errors': errors}
            if errors:
                messages.warning(request, f'Procesado con errores: {len(errors)} problema(s).')
            return render(request, self.template_name, context)

        missing_brand_keys = set()
        brand_keys_by_record = []
        for i, sku, description, brand_name, country in records:
            brand = None
            if brand_name:
                key = (country.id, brand_name.casefold())
                brand = brands.get(key)
                if brand is None:
                    if create_brands:
                        missing_brand_keys.add((country.id, brand_name, country))
                    else:
                        errors.append(f'Fila {i}: Marca "{brand_name}" no existe en {country.code}')
                        continue
            brand_keys_by_record.append((i, sku, description, brand_name, country, brand))

        with transaction.atomic():
            if missing_brand_keys:
                Brand.objects.bulk_create(
                    [Brand(name=name, country=country) for country_id, name, country in missing_brand_keys],
                    batch_size=500,
                )
                country_ids = {country.id for country in (item[2] for item in missing_brand_keys)}
                for brand in Brand.objects.filter(country_id__in=country_ids):
                    brands[(brand.country_id, brand.name.casefold())] = brand

            record_keys = {(sku, country.id) for i, sku, description, brand_name, country, brand in brand_keys_by_record}
            existing_map = {}
            for country_id in {country_id for sku, country_id in record_keys}:
                skus = {sku for sku_key, cid in record_keys if cid == country_id for sku in [sku_key]}
                for start in range(0, len(skus), 500):
                    chunk = list(skus)[start:start + 500]
                    for product in Product.objects.filter(country_id=country_id, sku__in=chunk):
                        existing_map[(product.sku, product.country_id)] = product

            new_products = []
            new_keys = set()
            to_update = {}
            update_fields = set()

            for i, sku, description, brand_name, country, brand in brand_keys_by_record:
                if brand_name and brand is None:
                    brand = brands.get((country.id, brand_name.casefold()))

                key = (sku, country.id)
                product = existing_map.get(key)
                if product is None and key in new_keys:
                    product = next(item for item in new_products if (item.sku, item.country_id) == key)

                if product:
                    changed = False
                    if product.description != description:
                        product.description = description
                        changed = True
                        update_fields.add('description')
                    if product.brand_id != (brand.id if brand else None):
                        product.brand = brand
                        changed = True
                        update_fields.add('brand')
                    if changed and product.pk:
                        to_update[product.pk] = product
                else:
                    product = Product(sku=sku, description=description, brand=brand, country=country)
                    new_products.append(product)
                    new_keys.add(key)
                    existing_map[key] = product

            if to_update:
                fields = [field for field in ('description', 'brand') if field in update_fields]
                Product.objects.bulk_update(list(to_update.values()), fields, batch_size=500)
            if new_products:
                Product.objects.bulk_create(new_products, batch_size=500)
            created_count = len(new_products)
            updated_count = len(to_update)

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
        return response1
