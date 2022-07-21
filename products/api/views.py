from django.db import transaction

from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from products.models import Product
from products.api.serializers import ProductReadSerializer, ProductSerializer


class StandartResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class ProductList(ListAPIView):
    queryset = Product.objects.all().order_by('category')
    serializer_class = ProductReadSerializer
    pagination_class = StandartResultPagination


class ProductCreate(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductFilter(APIView):
    def post(self, *args, **kwargs):
        data = self.request.data
        filter_data = {}
        
        for key, value in data.items():
            if value != '' and key != 'csrfmiddlewaretoken':
                filter_data[key] = value

        products_filtered = Product.objects.filter(**filter_data)

        # paginator = StandartResultPagination()
        # result_page = paginator.paginate_queryset(products_filtered.order_by('id'), self.request)
        serializer = ProductReadSerializer(products_filtered, many=True)

        # return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
