from django.urls import path
from api.v1.views.product_views import (
    CategoryListView, CategoryDetailView,
    ProductListView, ProductDetailView,
    ProductSearchView, ProductLowStockView
)

urlpatterns = [
    # Catégories
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(), name='categories-detail'),
    
    # Produits
    path('products/', ProductListView.as_view(), name='products-list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='products-detail'),
    path('products/search/', ProductSearchView.as_view(), name='products-search'),
    path('products/low-stock/', ProductLowStockView.as_view(), name='products-low-stock'),
]
