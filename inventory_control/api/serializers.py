from rest_framework import serializers

from inventory_control.models import Inventory, Warehouse, Employee, InventoryCount, ProductStatus, StorageType
from products.api.serializers import ProductReadSerializer
from rest_framework import serializers as drf_serializers


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
 

class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = '__all__'


class InventoryReadSerializer(InventorySerializer):
    absolute_url = serializers.SerializerMethodField()
    warehouse = serializers.CharField(source='warehouse.name')
    employee = serializers.SerializerMethodField()
    store = serializers.CharField(source='store.username')
    status_display = serializers.SerializerMethodField()

    def get_absolute_url(self, instance):
        absolute_url = instance.get_absolute_url()
        return absolute_url

    def get_employee(self, instance):
        return f"{instance.employee.first_name} {instance.employee.last_name}"

    def get_status_display(self, instance):
        return instance.get_status_display()


class InventoryCountSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(initial=True)
    
    class Meta:
        model = InventoryCount
        fields = '__all__'

    def validate(self, attrs):
        product_status = attrs.get('product_status') or getattr(self.instance, 'product_status', None)
        image = attrs.get('image', None)

        # Handle PATCH when image not in attrs but instance may have one
        has_image = bool(image) or bool(getattr(self.instance, 'image', None))

        if product_status is not None:
            status_name = (product_status.name or '').strip().lower()
            # consider both with and without accent
            if status_name in ('roto', 'dañado', 'danado') and not has_image:
                raise drf_serializers.ValidationError({
                    'image': 'La imagen es obligatoria cuando el estado es Roto o Dañado.'
                })

        return attrs


class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = '__all__'


class StorageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageType
        fields = '__all__'


class InventoryCountReadSerializer(InventoryCountSerializer):
    created = serializers.DateTimeField(format="%d-%m-%Y")
    creator = serializers.CharField(source='creator.username')
    product = ProductReadSerializer()
    product_status = ProductStatusSerializer()
    storage_type = StorageTypeSerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        if instance.image:
            try:
                return instance.image.url
            except Exception:
                return None
        return None
    
    
    
