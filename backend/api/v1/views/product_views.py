"""Vues pour la gestion des produits."""
from rest_framework import views, status
from rest_framework.response import Response
from django.db.models import Q, Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.products.models import Product, Category
from api.v1.serializers.product_serializers import (
    CategorySerializer, CategoryTreeSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, StockSearchSerializer
)
from api.v1.permissions import IsOperator, IsManager, ReadOnly
from core.utils.response import success_response, error_response, paginated_response


class CategoryListView(views.APIView):
    """Liste et création des catégories."""
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperator()]
        return [IsManager()]
    
    @swagger_auto_schema(operation_description="Liste toutes les catégories")
    def get(self, request):
        categories = Category.objects.filter(is_deleted=False).order_by('sort_order', 'name')
        
        # Mode arbre si demandé
        if request.query_params.get('tree') == 'true':
            root_categories = categories.filter(parent__isnull=True)
            serializer = CategoryTreeSerializer(root_categories, many=True)
        else:
            serializer = CategorySerializer(categories, many=True)
        
        return success_response(data=serializer.data)
    
    @swagger_auto_schema(
        operation_description="Crée une catégorie",
        request_body=CategorySerializer
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        serializer.save()
        return success_response(data=serializer.data, message="Catégorie créée", status_code=201)


class CategoryDetailView(views.APIView):
    """Détail, mise à jour, suppression d'une catégorie."""
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperator()]
        return [IsManager()]
    
    def get_object(self, pk):
        try:
            return Category.objects.get(id=pk, is_deleted=False)
        except Category.DoesNotExist:
            return None
    
    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message="Catégorie introuvable", status_code=404)
        serializer = CategorySerializer(category)
        return success_response(data=serializer.data)
    
    def patch(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message="Catégorie introuvable", status_code=404)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        serializer.save()
        return success_response(data=serializer.data, message="Catégorie mise à jour")
    
    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message="Catégorie introuvable", status_code=404)
        if category.products.filter(is_deleted=False).exists():
            return error_response(message="Impossible de supprimer: des produits sont associés", status_code=409)
        category.soft_delete()
        return success_response(message="Catégorie supprimée")


class ProductListView(views.APIView):
    """Liste et création des produits."""
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperator()]
        return [IsManager()]
    
    @swagger_auto_schema(
        operation_description="Liste les produits avec filtres",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid'),
            openapi.Parameter('supplier', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid'),
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('stock_status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        queryset = Product.objects.filter(is_deleted=False).select_related('category', 'supplier')
        
        # Filtres
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(reference__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(brand__icontains=search)
            )
        
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        supplier = request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtre par statut de stock
        stock_status = request.query_params.get('stock_status')
        if stock_status:
            if stock_status == 'low_stock':
                queryset = [p for p in queryset if p.is_low_stock]
            elif stock_status == 'out_of_stock':
                queryset = [p for p in queryset if sum(s.quantity for s in p.stocks.filter(is_deleted=False)) <= 0]
        
        # Tri
        ordering = request.query_params.get('ordering', 'name')
        queryset = queryset.order_by(ordering)
        
        return paginated_response(queryset, ProductListSerializer, request)
    
    @swagger_auto_schema(
        operation_description="Crée un produit",
        request_body=ProductCreateUpdateSerializer
    )
    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        product = serializer.save()
        output = ProductDetailSerializer(product)
        return success_response(data=output.data, message="Produit créé", status_code=201)


class ProductDetailView(views.APIView):
    """Détail, mise à jour, suppression d'un produit."""
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperator()]
        return [IsManager()]
    
    def get_object(self, pk):
        try:
            return Product.objects.get(id=pk, is_deleted=False)
        except Product.DoesNotExist:
            return None
    
    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return error_response(message="Produit introuvable", status_code=404)
        serializer = ProductDetailSerializer(product)
        return success_response(data=serializer.data)
    
    def patch(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return error_response(message="Produit introuvable", status_code=404)
        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        serializer.save()
        output = ProductDetailSerializer(product)
        return success_response(data=output.data, message="Produit mis à jour")
    
    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return error_response(message="Produit introuvable", status_code=404)
        product.soft_delete()
        return success_response(message="Produit supprimé")


class ProductSearchView(views.APIView):
    """Recherche avancée de produits."""
    
    permission_classes = [IsOperator]
    
    @swagger_auto_schema(
        request_body=StockSearchSerializer,
        operation_description="Recherche avancée"
    )
    def post(self, request):
        serializer = StockSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        
        query = serializer.validated_data['query']
        products = Product.objects.filter(is_deleted=False).filter(
            Q(name__icontains=query) |
            Q(reference__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode=query)
        )
        
        output = ProductListSerializer(products[:50], many=True)
        return success_response(data={'results': output.data, 'count': products.count()})


class ProductLowStockView(views.APIView):
    """Liste des produits en stock bas."""
    
    permission_classes = [IsManager]
    
    def get(self, request):
        products = Product.objects.filter(is_deleted=False, status='ACTIVE')
        low_stock = [p for p in products if p.is_low_stock]
        
        data = [{
            'product': ProductListSerializer(p).data,
            'total_stock': sum(s.quantity for s in p.stocks.filter(is_deleted=False)),
            'min_stock': p.min_stock,
            'reorder_point': p.reorder_point,
            'suggested_order': p.optimal_quantity - sum(s.quantity for s in p.stocks.filter(is_deleted=False))
        } for p in low_stock]
        
        return success_response(data={'results': data, 'count': len(data)})
