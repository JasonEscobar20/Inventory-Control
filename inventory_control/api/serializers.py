from rest_framework import serializers

from inventory_control.models import Inventory, Warehouse, Employee, InventoryCount, MeasurementUnit, ProductStatus, Side, StorageType
from products.api.serializers import ProductReadSerializer


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
    employee = serializers.CharField(source='employee.first_name')
    store = serializers.CharField(source='store.username')

    def get_absolute_url(self, instance):
        absolute_url = instance.get_absolute_url()
        return absolute_url


class InventoryCountSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(initial=True)
    
    class Meta:
        model = InventoryCount
        fields = '__all__'


class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = '__all__'


class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = '__all__'


class SideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Side
        fields = '__all__'


class StorageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageType
        fields = '__all__'


class InventoryCountReadSerializer(InventoryCountSerializer):
    created = serializers.DateTimeField(format="%d-%m-%Y")
    creator = serializers.CharField(source='creator.username')
    product = ProductReadSerializer()
    measurement_unit = MeasurementUnitSerializer()
    product_status = ProductStatusSerializer()
    side = SideSerializer()
    storage_type = StorageTypeSerializer()
    
    
    
