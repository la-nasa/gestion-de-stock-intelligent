"""
Tests pour le module produits.
"""
import pytest
from rest_framework import status
from tests.factories.models import (
    ProductFactory, CategoryFactory, WarehouseFactory,
    UserFactory
)
from apps.products.models import Product, Category
from apps.stock_movements.models import Stock


class TestProductModel:
    """Tests du modèle Product."""
    
    def test_create_product(self, db):
        """Test création produit."""
        category = CategoryFactory()
        product = ProductFactory(category=category)
        
        assert product.name is not None
        assert product.reference is not None
        assert product.sku is not None
        assert product.category == category
    
    def test_product_total_value(self, db):
        """Test calcul valeur totale."""
        product = ProductFactory(unit_price=5000)
        warehouse = WarehouseFactory()
        
        Stock.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=10,
            unit_price=5000,
        )
        
        assert product.total_value == 50000
    
    def test_product_is_low_stock(self, db):
        """Test détection stock bas."""
        product = ProductFactory(min_stock=20)
        warehouse = WarehouseFactory()
        
        Stock.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=5,
            unit_price=1000,
        )
        
        assert product.is_low_stock is True


class TestProductAPI:
    """Tests API produits."""
    
    def test_list_products(self, db, authenticated_client):
        """Test liste produits."""
        client, user = authenticated_client
        ProductFactory.create_batch(5)
        
        response = client.get('/api/v1/products/')
        assert response.status_code == 200
    
    def test_create_product_requires_manager(self, db, operator_client):
        """Test création produit nécessite manager."""
        client, user = operator_client
        category = CategoryFactory()
        
        response = client.post('/api/v1/products/', {
            'name': 'Nouveau produit',
            'reference': 'REF-NEW',
            'sku': 'SKU-NEW',
            'category_id': str(category.id),
            'unit': 'PIECE',
            'unit_price': 5000,
        }, format='json')
        
        assert response.status_code == 403
    
    def test_create_product_as_manager(self, db, manager_client):
        """Test création produit en tant que manager."""
        client, user = manager_client
        category = CategoryFactory()
        
        response = client.post('/api/v1/products/', {
            'name': 'Produit Manager',
            'reference': 'REF-MGR',
            'sku': 'SKU-MGR',
            'category_id': str(category.id),
            'unit': 'PIECE',
            'unit_price': 7500,
        }, format='json')
        
        assert response.status_code == 201
    
    def test_get_product_detail(self, db, authenticated_client):
        """Test détail produit."""
        client, user = authenticated_client
        product = ProductFactory()
        
        response = client.get(f'/api/v1/products/{product.id}/')
        assert response.status_code == 200
        assert response.data['data']['name'] == product.name
    
    def test_update_product(self, db, manager_client):
        """Test mise à jour produit."""
        client, user = manager_client
        product = ProductFactory()
        
        response = client.patch(
            f'/api/v1/products/{product.id}/',
            {'name': 'Nom modifié'},
            format='json'
        )
        
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.name == 'Nom modifié'
    
    def test_delete_product(self, db, manager_client):
        """Test suppression produit (soft delete)."""
        client, user = manager_client
        product = ProductFactory()
        
        response = client.delete(f'/api/v1/products/{product.id}/')
        assert response.status_code == 200
        
        product.refresh_from_db()
        assert product.is_deleted is True
    
    def test_search_products(self, db, authenticated_client):
        """Test recherche produits."""
        client, user = authenticated_client
        ProductFactory(name='Ordinateur Dell')
        ProductFactory(name='Imprimante HP')
        ProductFactory(name='Papier A4')
        
        response = client.get('/api/v1/products/?search=Dell')
        assert response.status_code == 200
    
    def test_low_stock_products(self, db, authenticated_client):
        """Test liste produits stock bas."""
        client, user = authenticated_client
        product = ProductFactory(min_stock=50)
        warehouse = WarehouseFactory()
        
        Stock.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=5,
            unit_price=1000,
        )
        
        response = client.get('/api/v1/products/low-stock/')
        assert response.status_code == 200