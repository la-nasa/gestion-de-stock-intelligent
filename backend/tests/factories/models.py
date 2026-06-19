"""
Factories pour les modèles de test.
"""
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.warehouses.models import Warehouse
from apps.suppliers.models import Supplier
from apps.departments.models import Department, Campus
from apps.stock_movements.models import Stock


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@test.cm')
    first_name = 'Test'
    last_name = 'User'
    matricule = factory.Sequence(lambda n: f'TST{n:04d}')
    role = 'OPERATOR'
    is_active = True
    
    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        obj.set_password('TestPass123!')
        obj.save()


class CampusFactory(DjangoModelFactory):
    class Meta:
        model = Campus
    
    name = 'Campus Principal'
    code = 'CAMPUS-01'
    city = 'Douala'


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
    
    name = factory.Sequence(lambda n: f'Département {n}')
    code = factory.Sequence(lambda n: f'DEPT-{n:02d}')
    campus = factory.SubFactory(CampusFactory)
    type = 'ACADEMIC'


class WarehouseFactory(DjangoModelFactory):
    class Meta:
        model = Warehouse
    
    name = factory.Sequence(lambda n: f'Entrepôt {n}')
    code = factory.Sequence(lambda n: f'WH-{n:02d}')
    campus = factory.SubFactory(CampusFactory)
    type = 'SECONDARY'


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Catégorie {n}')
    code = factory.Sequence(lambda n: f'CAT-{n:02d}')


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f'Produit {n}')
    reference = factory.Sequence(lambda n: f'REF-{n:04d}')
    sku = factory.Sequence(lambda n: f'SKU-{n:04d}')
    category = factory.SubFactory(CategoryFactory)
    unit = 'PIECE'
    unit_price = 10000
    min_stock = 10
    max_stock = 100


class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = Supplier
    
    name = factory.Sequence(lambda n: f'Fournisseur {n}')
    code = factory.Sequence(lambda n: f'SUP-{n:02d}')
    email = factory.Sequence(lambda n: f'supplier{n}@test.cm')