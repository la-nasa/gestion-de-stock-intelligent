"""Serializers pour les stocks et mouvements."""
from rest_framework import serializers
from apps.stock_movements.models import Stock, StockMovement
from apps.stock_entries.models import StockEntry, StockEntryLine
from apps.stock_outputs.models import StockOutput, StockOutputLine
from apps.transfers.models import Transfer, TransferLine


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_reference = serializers.CharField(source='product.reference', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'product_reference',
            'warehouse', 'warehouse_name',
            'quantity', 'reserved_quantity', 'available_quantity',
            'unit_price', 'location', 'status',
            'last_inventory_date', 'last_movement_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'available_quantity', 'created_at', 'updated_at']
    
    def get_status(self, obj):
        if obj.quantity <= 0:
            return 'out_of_stock'
        elif obj.quantity <= obj.product.min_stock:
            return 'low'
        return 'normal'


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='stock.product.name', read_only=True)
    warehouse_name = serializers.CharField(source='stock.warehouse.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'movement_type', 'reason',
            'stock', 'product_name', 'warehouse_name',
            'quantity', 'unit_price', 'total_price',
            'reference_document',
            'performed_by', 'performed_by_name',
            'is_validated', 'validated_at',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'is_validated', 'created_at']


class StockEntrySerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StockEntry
        fields = [
            'id', 'reference', 'status',
            'warehouse', 'warehouse_name',
            'supplier', 'supplier_name',
            'purchase_order', 'delivery_note', 'invoice_number',
            'entry_date', 'total_amount',
            'received_by', 'validated_by', 'validated_at',
            'lines_count', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'reference', 'entry_date', 'created_at']
    
    def get_lines_count(self, obj):
        return obj.lines.count()


class StockEntryLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockEntryLine
        fields = [
            'id', 'entry', 'product', 'product_name',
            'quantity', 'unit_price', 'total_price',
            'location', 'batch_number', 'expiry_date'
        ]
        read_only_fields = ['id', 'total_price']


class StockOutputSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = StockOutput
        fields = [
            'id', 'reference', 'status', 'reason',
            'warehouse', 'warehouse_name',
            'department', 'department_name',
            'recipient', 'output_date', 'total_amount',
            'issued_by', 'received_by', 'validated_by',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'reference', 'output_date', 'created_at']


class TransferSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source_warehouse.name', read_only=True)
    destination_name = serializers.CharField(source='destination_warehouse.name', read_only=True)
    
    class Meta:
        model = Transfer
        fields = [
            'id', 'reference', 'status',
            'source_warehouse', 'source_name',
            'destination_warehouse', 'destination_name',
            'requested_by', 'approved_by',
            'approved_at', 'shipped_at', 'received_at',
            'total_items', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'reference', 'created_at']
