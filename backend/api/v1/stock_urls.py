from django.urls import path
from api.v1.views.stock_views import (
    StockListView, StockDetailView,
    StockMovementListView,
    StockEntryListView, StockEntryDetailView, StockEntryCreateView,
    StockOutputListView, StockOutputCreateView,
    TransferListView, TransferCreateView
)
from api.v1.views.supplier_views import SupplierListView, SupplierDetailView, SupplierCreateView
from api.v1.views.order_views import PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderCreateView
from api.v1.views.product_views import ProductCreateView

urlpatterns = [
    path("stocks/", StockListView.as_view(), name="stocks-list"),
    path("stocks/<uuid:pk>/", StockDetailView.as_view(), name="stocks-detail"),
    path("movements/", StockMovementListView.as_view(), name="movements-list"),
    path("stock-entries/", StockEntryListView.as_view(), name="stock-entries-list"),
    path("stock-entries/<uuid:pk>/", StockEntryDetailView.as_view(), name="stock-entries-detail"),
    path("stock-entries/create/", StockEntryCreateView.as_view(), name="stock-entries-create"),
    path("stock-outputs/", StockOutputListView.as_view(), name="stock-outputs-list"),
    path("stock-outputs/create/", StockOutputCreateView.as_view(), name="stock-outputs-create"),
    path("transfers/", TransferListView.as_view(), name="transfers-list"),
    path("transfers/create/", TransferCreateView.as_view(), name="transfers-create"),
    path("suppliers/", SupplierListView.as_view(), name="suppliers-list"),
    path("suppliers/<uuid:pk>/", SupplierDetailView.as_view(), name="suppliers-detail"),
    path("suppliers/create/", SupplierCreateView.as_view(), name="suppliers-create"),
    path("purchase-orders/", PurchaseOrderListView.as_view(), name="purchase-orders-list"),
    path("purchase-orders/<uuid:pk>/", PurchaseOrderDetailView.as_view(), name="purchase-orders-detail"),
    path("purchase-orders/create/", PurchaseOrderCreateView.as_view(), name="purchase-orders-create"),
    path("products/create/", ProductCreateView.as_view(), name="products-create"),
]
