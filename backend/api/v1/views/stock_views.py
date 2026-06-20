"""Vues pour la gestion des stocks."""
from rest_framework import views, status
from drf_yasg.utils import swagger_auto_schema

from apps.stock_movements.models import Stock, StockMovement
from apps.stock_entries.models import StockEntry, StockEntryLine
from apps.stock_outputs.models import StockOutput, StockOutputLine
from apps.transfers.models import Transfer, TransferLine
from api.v1.serializers.stock_serializers import (
    StockSerializer, StockMovementSerializer,
    StockEntrySerializer, StockEntryLineSerializer,
    StockOutputSerializer, TransferSerializer
)
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response, paginated_response


class StockListView(views.APIView):
    """Liste des stocks."""
    
    permission_classes = [IsOperator]
    
    def get(self, request):
        queryset = Stock.objects.filter(is_deleted=False).select_related('product', 'warehouse')
        
        # Filtres
        warehouse = request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        
        product = request.query_params.get('product')
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Statut stock
        stock_status = request.query_params.get('status')
        if stock_status == 'low':
            queryset = [s for s in queryset if s.quantity <= s.product.min_stock]
        elif stock_status == 'out':
            queryset = [s for s in queryset if s.quantity <= 0]
        
        return paginated_response(queryset, StockSerializer, request)


class StockDetailView(views.APIView):
    """Détail d'un stock."""
    
    permission_classes = [IsOperator]
    
    def get(self, request, pk):
        try:
            stock = Stock.objects.get(id=pk, is_deleted=False)
        except Stock.DoesNotExist:
            return error_response(message="Stock introuvable", status_code=404)
        
        serializer = StockSerializer(stock)
        return success_response(data=serializer.data)


class StockMovementListView(views.APIView):
    """Liste des mouvements de stock."""
    
    permission_classes = [IsOperator]
    
    def get(self, request):
        queryset = StockMovement.objects.filter(is_deleted=False).select_related(
            'stock__product', 'stock__warehouse', 'performed_by'
        )
        
        # Filtres
        movement_type = request.query_params.get('type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        stock_id = request.query_params.get('stock')
        if stock_id:
            queryset = queryset.filter(stock_id=stock_id)
        
        is_validated = request.query_params.get('validated')
        if is_validated is not None:
            queryset = queryset.filter(is_validated=is_validated.lower() == 'true')
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return paginated_response(queryset, StockMovementSerializer, request)
    
    @swagger_auto_schema(
        operation_description="Crée un mouvement de stock",
        request_body=StockMovementSerializer
    )
    def post(self, request):
        serializer = StockMovementSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        movement = serializer.save(performed_by=request.user)
        output = StockMovementSerializer(movement)
        return success_response(data=output.data, message="Mouvement créé", status_code=201)


class StockMovementValidateView(views.APIView):
    """Validation d'un mouvement de stock."""
    
    permission_classes = [IsManager]
    
    def post(self, request, pk):
        try:
            movement = StockMovement.objects.get(id=pk, is_deleted=False)
        except StockMovement.DoesNotExist:
            return error_response(message="Mouvement introuvable", status_code=404)
        
        if movement.is_validated:
            return error_response(message="Déjà validé", status_code=409)
        
        try:
            movement.validate(request.user)
            return success_response(message="Mouvement validé")
        except Exception as e:
            return error_response(message=str(e), status_code=400)


class StockEntryListView(views.APIView):
    """Liste et création des entrées de stock."""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [IsOperator()]
    
    def get(self, request):
        queryset = StockEntry.objects.filter(is_deleted=False).select_related('warehouse', 'supplier')
        return paginated_response(queryset, StockEntrySerializer, request)
    
    @swagger_auto_schema(request_body=StockEntrySerializer)
    def post(self, request):
        serializer = StockEntrySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        entry = serializer.save(received_by=request.user)
        return success_response(data=StockEntrySerializer(entry).data, message="Entrée créée", status_code=201)


class StockEntryDetailView(views.APIView):
    """Détail d'une entrée de stock avec ses lignes."""
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsManager()]
        return [IsOperator()]
    
    def get(self, request, pk):
        try:
            entry = StockEntry.objects.get(id=pk, is_deleted=False)
        except StockEntry.DoesNotExist:
            return error_response(message="Entrée introuvable", status_code=404)
        
        serializer = StockEntrySerializer(entry)
        lines = StockEntryLineSerializer(entry.lines.all(), many=True)
        
        return success_response(data={
            'entry': serializer.data,
            'lines': lines.data
        })
    
    @swagger_auto_schema(request_body=StockEntryLineSerializer)
    def post(self, request, pk):
        """Ajoute une ligne à l'entrée."""
        try:
            entry = StockEntry.objects.get(id=pk, is_deleted=False, status='DRAFT')
        except StockEntry.DoesNotExist:
            return error_response(message="Entrée introuvable ou non modifiable", status_code=404)
        
        serializer = StockEntryLineSerializer(data={**request.data, 'entry': entry.id})
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        serializer.save()
        return success_response(data=serializer.data, message="Ligne ajoutée", status_code=201)


class StockOutputListView(views.APIView):
    """Liste et création des sorties de stock."""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [IsOperator()]
    
    def get(self, request):
        queryset = StockOutput.objects.filter(is_deleted=False).select_related('warehouse', 'department')
        return paginated_response(queryset, StockOutputSerializer, request)
    
    @swagger_auto_schema(request_body=StockOutputSerializer)
    def post(self, request):
        serializer = StockOutputSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        output = serializer.save(issued_by=request.user)
        return success_response(data=StockOutputSerializer(output).data, message="Sortie créée", status_code=201)


class TransferListView(views.APIView):
    """Liste et création des transferts."""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [IsOperator()]
    
    def get(self, request):
        queryset = Transfer.objects.filter(is_deleted=False).select_related(
            'source_warehouse', 'destination_warehouse'
        )
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return paginated_response(queryset, TransferSerializer, request)
    
    @swagger_auto_schema(request_body=TransferSerializer)
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        transfer = serializer.save(requested_by=request.user)
        return success_response(data=TransferSerializer(transfer).data, message="Transfert créé", status_code=201)


class StockEntryCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        from apps.warehouses.models import Warehouse
        from apps.products.models import Product
        try:
            wh = Warehouse.objects.get(id=request.data.get("warehouse_id"))
            entry = StockEntry.objects.create(warehouse=wh, received_by=request.user, notes=request.data.get("notes", ""))
            items = request.data.get("items", [])
            for item in items:
                product = Product.objects.get(id=item.get("product_id"))
                StockEntryLine.objects.create(entry=entry, product=product, quantity=item.get("quantity", 0), unit_price=item.get("unit_price", 0))
            return success_response(data={"id": str(entry.id), "reference": entry.reference}, message="Entrée créée", status_code=201)
        except Exception as e:
            return error_response(message=str(e), status_code=400)

class StockOutputCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        from apps.warehouses.models import Warehouse
        from apps.products.models import Product
        try:
            wh = Warehouse.objects.get(id=request.data.get("warehouse_id"))
            output = StockOutput.objects.create(warehouse=wh, reason=request.data.get("reason", "INTERNAL_USE"), issued_by=request.user, notes=request.data.get("notes", ""))
            items = request.data.get("items", [])
            for item in items:
                product = Product.objects.get(id=item.get("product_id"))
                StockOutputLine.objects.create(output=output, product=product, quantity=item.get("quantity", 0), unit_price=item.get("unit_price", 0))
            return success_response(data={"id": str(output.id), "reference": output.reference}, message="Sortie créée", status_code=201)
        except Exception as e:
            return error_response(message=str(e), status_code=400)

class TransferCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        from apps.warehouses.models import Warehouse
        from apps.products.models import Product
        try:
            src = Warehouse.objects.get(id=request.data.get("source_warehouse_id"))
            dst = Warehouse.objects.get(id=request.data.get("destination_warehouse_id"))
            transfer = Transfer.objects.create(source_warehouse=src, destination_warehouse=dst, requested_by=request.user, notes=request.data.get("notes", ""))
            items = request.data.get("items", [])
            for item in items:
                product = Product.objects.get(id=item.get("product_id"))
                TransferLine.objects.create(transfer=transfer, product=product, quantity=item.get("quantity", 0), unit_price=item.get("unit_price", 0))
            return success_response(data={"id": str(transfer.id), "reference": transfer.reference}, message="Transfert créé", status_code=201)
        except Exception as e:
            return error_response(message=str(e), status_code=400)