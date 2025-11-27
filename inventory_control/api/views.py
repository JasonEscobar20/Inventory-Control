from django.db import transaction


from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from inventory_control.models import Inventory, InventoryCount
from geo.models import UserProfile
from inventory_control.api.serializers import InventorySerializer, InventoryReadSerializer, InventoryCountSerializer, InventoryCountReadSerializer



class StandartResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class InventoryList(ListAPIView):
    serializer_class = InventoryReadSerializer
    pagination_class = StandartResultPagination

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        qs = Inventory.objects.all().order_by('-id')
        if profile and profile.country:
            qs = qs.filter(country=profile.country)
        # Filters
        warehouse_id = self.request.query_params.get('warehouse')
        employee_id = self.request.query_params.get('employee')
        date = self.request.query_params.get('date')
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if date:
            qs = qs.filter(inventory_date=date)
        return qs


class InventoryCreate(CreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        serializer.save(country=country)


## INVENTORY COUNTS
class InventoryCountCreate(CreateAPIView):
    queryset = InventoryCount.objects.all()
    serializer_class = InventoryCountSerializer

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        serializer.save(country=country, creator=self.request.user)


class InventoryCountList(ListAPIView):
    serializer_class = InventoryCountReadSerializer
    pagination_class = StandartResultPagination

    def get_queryset(self):
        inventory_id = self.kwargs['inventory_id']
        profile = getattr(self.request.user, 'profile', None)
        base_qs = Inventory.objects.all()
        if profile and profile.country:
            base_qs = base_qs.filter(country=profile.country)
        inventory = base_qs.get(id=inventory_id)
        inventory_counts = inventory.inventory_records.all().order_by('id')

        print(inventory_counts.last())

        return inventory_counts


class InventoryCountUpdate(UpdateAPIView):
    # queryset = InventoryCount.objects.all()
    serializer_class = InventoryCountSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        instance = InventoryCount.objects.filter(id=pk)
        return instance

    
class InventoryCountFilter(APIView):
    def post(self, *args, **kwargs):
        data = self.request.data
        filter_data = {}
        end_date = data.get('end_date', '')

        for key, value in data.items():
            if value != '':
                if key == 'sku':
                    filter_data['product__sku'] = value
                if key == 'product_status':
                    filter_data['product_status'] = value

                if key == 'storage_type':
                    filter_data['storage_type'] = value

        profile = getattr(self.request.user, 'profile', None)
        qs = InventoryCount.objects.filter(**filter_data)
        if profile and profile.country:
            qs = qs.filter(country=profile.country)
        inventory_counts_filtered = qs

        # paginator = StandartResultPagination()
        # result_page = paginator.paginate_queryset(products_filtered.order_by('id'), self.request)
        serializer = InventoryCountReadSerializer(inventory_counts_filtered, many=True)

        # return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InventoryStatusUpdate(APIView):
    """Endpoint to transition inventory status in allowed order."""
    def post(self, request, *args, **kwargs):
        inventory_id = kwargs.get('pk')
        try:
            new_status = int(request.data.get('status', 0))
        except (TypeError, ValueError):
            return Response({'detail': 'Estado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Country restriction
        profile = getattr(request.user, 'profile', None)
        qs = Inventory.objects.all()
        if profile and profile.country:
            qs = qs.filter(country=profile.country)

        try:
            inv = qs.get(pk=inventory_id)
        except Inventory.DoesNotExist:
            return Response({'detail': 'Inventario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            inv.apply_transition(new_status, user=request.user)
            inv.save()
        except ValueError as ex:
            return Response({'detail': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InventoryReadSerializer(inv)
        return Response(serializer.data, status=status.HTTP_200_OK)