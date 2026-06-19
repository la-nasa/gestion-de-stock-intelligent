"""Serializers pour les produits et catégories."""
from rest_framework import serializers
from apps.products.models import Product, Category
from apps.suppliers.models import Supplier
from apps.products.models import Category


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'code', 'description',
            'parent', 'icon', 'level', 'sort_order',
            'is_active', 'children_count', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'level', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.filter(is_deleted=False).count()
    
    def get_products_count(self, obj):
        return obj.products.filter(is_deleted=False).count()


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'icon', 'children']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True, is_deleted=False)
        return CategoryTreeSerializer(children, many=True).data if children.exists() else []


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'reference', 'sku', 'barcode',
            'category', 'category_name', 'brand', 'model_number',
            'unit', 'unit_price', 'currency',
            'total_stock', 'stock_status', 'min_stock',
            'status', 'supplier', 'supplier_name',
            'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_stock(self, obj):
        return sum(s.quantity for s in obj.stocks.filter(is_deleted=False))
    
    def get_stock_status(self, obj):
        total = self.get_total_stock(obj)
        if total <= 0:
            return 'out_of_stock'
        elif total <= obj.min_stock:
            return 'low_stock'
        elif total >= obj.max_stock:
            return 'overstocked'
        return 'normal'


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    stocks = serializers.SerializerMethodField()
    total_stock_value = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'reference', 'sku', 'barcode',
            'category', 'category_id', 'brand', 'model_number',
            'description', 'specifications',
            'unit', 'unit_price', 'currency',
            'min_stock', 'max_stock', 'reorder_point', 'optimal_quantity',
            'status', 'supplier',
            'requires_batch', 'requires_expiry', 'warranty_months',
            'image', 'datasheet',
            'stocks', 'total_stock_value', 'qr_code_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_stocks(self, obj):
        stocks = obj.stocks.filter(is_deleted=False).select_related('warehouse')
        return [{
            'warehouse_id': str(stock.warehouse_id),
            'warehouse_name': stock.warehouse.name,
            'quantity': stock.quantity,
            'reserved_quantity': stock.reserved_quantity,
            'available_quantity': stock.available_quantity,
            'location': stock.location,
            'unit_price': str(stock.unit_price),
            'total_value': str(stock.total_value)
        } for stock in stocks]
    
    def get_total_stock_value(self, obj):
        return str(obj.total_value)
    
    def get_qr_code_url(self, obj):
        if hasattr(obj, 'qr_code') and obj.qr_code.image:
            return obj.qr_code.image.url
        return None
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        validated_data['category'] = category
        return super().create(validated_data)


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(required=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'reference', 'sku', 'barcode',
            'category_id', 'brand', 'model_number',
            'description', 'specifications',
            'unit', 'unit_price', 'currency',
            'min_stock', 'max_stock', 'reorder_point', 'optimal_quantity',
            'status', 'supplier',
            'requires_batch', 'requires_expiry', 'warranty_months',
            'image', 'datasheet'
        ]
    
    def validate_category_id(self, value):
        try:
            category = Category.objects.get(id=value, is_active=True)
            return category
        except Category.DoesNotExist:
            raise serializers.ValidationError("Catégorie introuvable.")
    
    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Ce SKU est déjà utilisé.")
        return value
    
    def create(self, validated_data):
        category = validated_data.pop('category_id')
        validated_data['category'] = category
        return super().create(validated_data)


class StockSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=2)
    category = serializers.UUIDField(required=False)
    warehouse = serializers.UUIDField(required=False)
    status = serializers.ChoiceField(
        choices=['normal', 'low_stock', 'out_of_stock', 'overstocked'],
        required=False
    )
