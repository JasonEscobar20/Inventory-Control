from rest_framework import serializers

from products.models import Product, Category, Type


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(initial=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductReadSerializer(ProductSerializer):
    absolute_url = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    type = serializers.CharField(source='type.name')

    def get_absolute_url(self, instance):
        absolute_url = instance.get_absolute_url()
        return absolute_url
