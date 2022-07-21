from django.db import transaction


from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from inventory_control.models import Inventory, InventoryCount
from inventory_control.api.serializers import InventorySerializer, InventoryReadSerializer, InventoryCountSerializer, InventoryCountReadSerializer



class StandartResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class InventoryList(ListAPIView):
    queryset = Inventory.objects.all().order_by('id')
    serializer_class = InventoryReadSerializer
    pagination_class = StandartResultPagination


class InventoryCreate(CreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer


## INVENTORY COUNTS
class InventoryCountCreate(CreateAPIView):
    queryset = InventoryCount.objects.all()
    serializer_class = InventoryCountSerializer


class InventoryCountList(ListAPIView):
    serializer_class = InventoryCountReadSerializer
    pagination_class = StandartResultPagination

    def get_queryset(self):
        inventory_id = self.kwargs['inventory_id']
        inventory = Inventory.objects.get(id=inventory_id)
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
        entry_date = data.get('entry_date', '')
        end_date = data.get('end_date', '')

        for key, value in data.items():
            if value != '':
                if key == 'sku':
                    filter_data['product__sku'] = value
                if key == 'product_status':
                    filter_data['product_status'] = value
                if key == 'measurement_unit':
                    filter_data['measurement_unit'] = value
                if key == 'storage_type':
                    filter_data['storage_type'] = value

        if entry_date != '' and end_date == '':
            filter_data['entry_date'] = entry_date
        
        if entry_date != '' and end_date != '':
            filter_data['entry_date__range'] = [entry_date, end_date]

        inventory_counts_filtered = InventoryCount.objects.filter(**filter_data)

        # paginator = StandartResultPagination()
        # result_page = paginator.paginate_queryset(products_filtered.order_by('id'), self.request)
        serializer = InventoryCountReadSerializer(inventory_counts_filtered, many=True)

        # return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)