from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(initial=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('country',)


class ProductReadSerializer(ProductSerializer):
    absolute_url = serializers.SerializerMethodField()
    brand = serializers.CharField(source='brand.name', read_only=True)

    def get_absolute_url(self, instance):
        absolute_url = instance.get_absolute_url()
        return absolute_url
