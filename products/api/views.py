from django.db import transaction

from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from products.models import Product
from geo.models import UserProfile
from products.api.serializers import ProductReadSerializer, ProductSerializer


class StandartResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class ProductList(ListAPIView):
    serializer_class = ProductReadSerializer
    pagination_class = StandartResultPagination

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        qs = Product.objects.order_by('id')
        if profile and profile.country:
            qs = qs.filter(country=profile.country)
        return qs


class ProductCreate(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        serializer.save(country=country)


class ProductFilter(APIView):
    def post(self, *args, **kwargs):
        data = self.request.data
        filter_data = {}
        
        for key, value in data.items():
            if value != '' and key != 'csrfmiddlewaretoken':
                filter_data[key] = value

        profile = getattr(self.request.user, 'profile', None)
        qs = Product.objects.filter(**filter_data)
        if profile and profile.country:
            qs = qs.filter(country=profile.country)
        products_filtered = qs

        # paginator = StandartResultPagination()
        # result_page = paginator.paginate_queryset(products_filtered.order_by('id'), self.request)
        serializer = ProductReadSerializer(products_filtered, many=True)

        # return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
