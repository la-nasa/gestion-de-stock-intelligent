"""Vues pour la gestion des produits."""
from rest_framework import views, status
from django.db.models import Q
from apps.products.models import Product
from apps.categories.models import Category
from api.v1.serializers.product_serializers import (
    CategorySerializer, CategoryTreeSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, StockSearchSerializer
)
from api.v1.permissions import IsOperator, IsManager
from core.utils.response import success_response, error_response, paginated_response


class CategoryListView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET": return [IsOperator()]
        return [IsManager()]

    def get(self, request):
        categories = Category.objects.filter(is_deleted=False).order_by("sort_order", "name")
        if request.query_params.get("tree") == "true":
            root = categories.filter(parent__isnull=True)
            serializer = CategoryTreeSerializer(root, many=True)
        else:
            serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid(): return error_response(message="Erreur validation", errors=serializer.errors, status_code=400)
        serializer.save()
        return success_response(data=serializer.data, message="Catégorie créée", status_code=201)


class CategoryDetailView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET": return [IsOperator()]
        return [IsManager()]

    def get_object(self, pk):
        try: return Category.objects.get(id=pk, is_deleted=False)
        except Category.DoesNotExist: return None

    def get(self, request, pk):
        cat = self.get_object(pk)
        if not cat: return error_response(message="Catégorie introuvable", status_code=404)
        return success_response(data=CategorySerializer(cat).data)

    def patch(self, request, pk):
        cat = self.get_object(pk)
        if not cat: return error_response(message="Catégorie introuvable", status_code=404)
        s = CategorySerializer(cat, data=request.data, partial=True)
        if not s.is_valid(): return error_response(message="Erreur validation", errors=s.errors, status_code=400)
        s.save()
        return success_response(data=s.data, message="Catégorie mise à jour")

    def delete(self, request, pk):
        cat = self.get_object(pk)
        if not cat: return error_response(message="Catégorie introuvable", status_code=404)
        if cat.products.filter(is_deleted=False).exists(): return error_response(message="Impossible: produits associés", status_code=409)
        cat.soft_delete()
        return success_response(message="Catégorie supprimée")


class ProductListView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET": return [IsOperator()]
        return [IsManager()]

    def get(self, request):
        qs = Product.objects.filter(is_deleted=False).select_related("category", "supplier")
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(reference__icontains=search) | Q(sku__icontains=search) | Q(barcode__icontains=search) | Q(brand__icontains=search))
        category = request.query_params.get("category")
        if category: qs = qs.filter(category_id=category)
        supplier = request.query_params.get("supplier")
        if supplier: qs = qs.filter(supplier_id=supplier)
        status_filter = request.query_params.get("status")
        if status_filter: qs = qs.filter(status=status_filter)
        stock_status = request.query_params.get("stock_status")
        if stock_status:
            if stock_status == "low_stock": qs = [p for p in qs if p.is_low_stock]
            elif stock_status == "out_of_stock": qs = [p for p in qs if sum(s.quantity for s in p.stocks.filter(is_deleted=False)) <= 0]
        ordering = request.query_params.get("ordering", "name")
        qs = qs.order_by(ordering)
        return paginated_response(qs, ProductListSerializer, request)

    def post(self, request):
        s = ProductCreateUpdateSerializer(data=request.data)
        if not s.is_valid(): return error_response(message="Erreur validation", errors=s.errors, status_code=400)
        product = s.save()
        return success_response(data=ProductDetailSerializer(product).data, message="Produit créé", status_code=201)


class ProductDetailView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET": return [IsOperator()]
        return [IsManager()]

    def get_object(self, pk):
        try: return Product.objects.get(id=pk, is_deleted=False)
        except Product.DoesNotExist: return None

    def get(self, request, pk):
        p = self.get_object(pk)
        if not p: return error_response(message="Produit introuvable", status_code=404)
        return success_response(data=ProductDetailSerializer(p).data)

    def patch(self, request, pk):
        p = self.get_object(pk)
        if not p: return error_response(message="Produit introuvable", status_code=404)
        s = ProductCreateUpdateSerializer(p, data=request.data, partial=True)
        if not s.is_valid(): return error_response(message="Erreur validation", errors=s.errors, status_code=400)
        s.save()
        return success_response(data=ProductDetailSerializer(p).data, message="Produit mis à jour")

    def delete(self, request, pk):
        p = self.get_object(pk)
        if not p: return error_response(message="Produit introuvable", status_code=404)
        p.soft_delete()
        return success_response(message="Produit supprimé")


class ProductSearchView(views.APIView):
    permission_classes = [IsOperator]

    def post(self, request):
        s = StockSearchSerializer(data=request.data)
        if not s.is_valid(): return error_response(message="Erreur validation", errors=s.errors, status_code=400)
        query = s.validated_data["query"]
        products = Product.objects.filter(is_deleted=False).filter(Q(name__icontains=query) | Q(reference__icontains=query) | Q(sku__icontains=query) | Q(barcode=query))
        output = ProductListSerializer(products[:50], many=True)
        return success_response(data={"results": output.data, "count": products.count()})


class ProductLowStockView(views.APIView):
    permission_classes = [IsManager]

    def get(self, request):
        products = Product.objects.filter(is_deleted=False, status="ACTIVE")
        low = [p for p in products if p.is_low_stock]
        data = [{"product": ProductListSerializer(p).data, "total_stock": sum(s.quantity for s in p.stocks.filter(is_deleted=False)), "min_stock": p.min_stock, "reorder_point": p.reorder_point, "suggested_order": p.optimal_quantity - sum(s.quantity for s in p.stocks.filter(is_deleted=False))} for p in low]
        return success_response(data={"results": data, "count": len(data)})

class ProductCreateView(views.APIView):
    permission_classes = [IsManager]
    def post(self, request):
        from apps.categories.models import Category
        try:
            cat = Category.objects.get(id=request.data.get("category_id"))
            p = Product.objects.create(
                name=request.data.get("name", ""),
                reference=request.data.get("reference", ""),
                sku=request.data.get("sku", ""),
                category=cat,
                unit_price=request.data.get("unit_price", 0),
                min_stock=request.data.get("min_stock", 0),
                max_stock=request.data.get("max_stock", 100),
                unit=request.data.get("unit", "PIECE"),
                brand=request.data.get("brand", ""),
                description=request.data.get("description", ""),
            )
            return success_response(data={"id": str(p.id), "name": p.name, "reference": p.reference}, message="Produit créé", status_code=201)
        except Category.DoesNotExist:
            return error_response(message="Catégorie introuvable", status_code=400)
        except Exception as e:
            return error_response(message=str(e), status_code=400)