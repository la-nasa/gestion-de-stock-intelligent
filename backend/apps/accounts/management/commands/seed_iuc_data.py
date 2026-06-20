"""
Commande de seeding complet pour l'IUC.
Peuple la base de données avec des données réalistes.
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.campuses.models import Campus
from apps.departments.models import Department
from apps.warehouses.models import Warehouse
from apps.categories.models import Category
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.stock_movements.models import Stock, StockMovement
from apps.roles.models import Role, Permission, RolePermission
from apps.purchase_orders.models import PurchaseOrder, PurchaseOrderLine
from apps.inventories.models import Inventory, InventoryLine
from apps.notifications.models import Notification
from apps.qr_codes.models import QRCode

User = get_user_model()


class Command(BaseCommand):
    help = 'Peuple la base avec des données réalistes de l\'IUC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprime toutes les données existantes avant le seeding',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force le seeding sans confirmation',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write(self.style.WARNING('Nettoyage des données existantes...'))
            self._clean_database()

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  SEEDING IUC INVENTORY SYSTEM'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        try:
            with transaction.atomic():
                self._seed_roles_permissions()
                self._seed_campuses()
                self._seed_departments()
                self._seed_users()
                self._seed_warehouses()
                self._seed_categories()
                self._seed_suppliers()
                self._seed_products()
                self._seed_stocks()
                self._seed_movements()
                self._seed_purchase_orders()
                self._seed_inventories()
                self._seed_qr_codes()

            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(self.style.SUCCESS('  ✅ SEEDING TERMINÉ AVEC SUCCÈS !'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self._print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors du seeding: {e}'))
            raise

    def _clean_database(self):
        """Nettoie toutes les tables."""
        models = [
            QRCode, Notification, InventoryLine, Inventory,
            PurchaseOrderLine, PurchaseOrder, StockMovement, Stock,
            Product, Category, Supplier, Warehouse,
            Department, Campus, User, RolePermission, Permission, Role,
        ]
        for model in models:
            model.objects.all().delete()
            self.stdout.write(f'  ✓ {model.__name__} nettoyé')

    def _seed_roles_permissions(self):
        self.stdout.write('\n📋 Création des rôles et permissions...')
        
        # Appeler la commande init_roles existante
        from django.core.management import call_command
        call_command('init_roles', verbosity=0)
        self.stdout.write('  ✓ Rôles et permissions initialisés')

    def _seed_campuses(self):
        self.stdout.write('\n🏛️ Création des campus...')
        
        campuses_data = [
            {
                'name': 'Campus Principal Douala',
                'code': 'CAMPUS-DLA',
                'address': 'Carrefour Ange Raphaël, Boulevard de la République',
                'city': 'Douala',
                'phone': '+237 233 42 12 34',
                'email': 'campus.douala@iuc.cm',
                'latitude': 4.0511,
                'longitude': 9.7068,
            },
            {
                'name': 'Campus Annexe Bonabéri',
                'code': 'CAMPUS-BON',
                'address': 'Quartier Bonabéri, face Mairie',
                'city': 'Douala',
                'phone': '+237 233 42 12 35',
                'email': 'campus.bonaberi@iuc.cm',
                'latitude': 4.0812,
                'longitude': 9.6734,
            },
            {
                'name': 'Campus Yaoundé',
                'code': 'CAMPUS-YDE',
                'address': 'Quartier Mvog-Mbi, rue 1.234',
                'city': 'Yaoundé',
                'phone': '+237 222 31 45 67',
                'email': 'campus.yaounde@iuc.cm',
                'latitude': 3.8480,
                'longitude': 11.5021,
            },
            {
                'name': 'Campus Bafoussam',
                'code': 'CAMPUS-BAF',
                'address': 'Quartier Tamdja, route de Bamenda',
                'city': 'Bafoussam',
                'phone': '+237 233 44 56 78',
                'email': 'campus.bafoussam@iuc.cm',
                'latitude': 5.4778,
                'longitude': 10.4176,
            },
        ]

        for data in campuses_data:
            Campus.objects.get_or_create(code=data['code'], defaults=data)
            self.stdout.write(f'  ✓ {data["name"]}')

    def _seed_departments(self):
        self.stdout.write('\n🏢 Création des départements...')
        
        campus_dla = Campus.objects.get(code='CAMPUS-DLA')
        campus_bon = Campus.objects.get(code='CAMPUS-BON')
        campus_yde = Campus.objects.get(code='CAMPUS-YDE')
        campus_baf = Campus.objects.get(code='CAMPUS-BAF')

        departments_data = [
            # Campus Principal Douala
            {'name': 'Direction Générale', 'code': 'DG', 'type': 'ADMINISTRATIVE', 'campus': campus_dla},
            {'name': 'Direction des Affaires Académiques', 'code': 'DAA', 'type': 'ACADEMIC', 'campus': campus_dla},
            {'name': 'Direction des Systèmes d\'Information', 'code': 'DSI', 'type': 'TECHNICAL', 'campus': campus_dla},
            {'name': 'Direction Financière', 'code': 'DF', 'type': 'ADMINISTRATIVE', 'campus': campus_dla},
            {'name': 'Département Informatique', 'code': 'INFO', 'type': 'ACADEMIC', 'campus': campus_dla},
            {'name': 'Département Gestion', 'code': 'GEST', 'type': 'ACADEMIC', 'campus': campus_dla},
            {'name': 'Département Marketing', 'code': 'MARK', 'type': 'ACADEMIC', 'campus': campus_dla},
            {'name': 'Département Comptabilité', 'code': 'COMPTA', 'type': 'ACADEMIC', 'campus': campus_dla},
            {'name': 'Département Ressources Humaines', 'code': 'DRH', 'type': 'ADMINISTRATIVE', 'campus': campus_dla},
            {'name': 'Service Logistique', 'code': 'LOG', 'type': 'TECHNICAL', 'campus': campus_dla},
            {'name': 'Bibliothèque Centrale', 'code': 'BIB', 'type': 'TECHNICAL', 'campus': campus_dla},
            
            # Campus Bonabéri
            {'name': 'Département Génie Civil', 'code': 'GC', 'type': 'ACADEMIC', 'campus': campus_bon},
            {'name': 'Département Électrotechnique', 'code': 'ELEC', 'type': 'ACADEMIC', 'campus': campus_bon},
            {'name': 'Département Télécommunications', 'code': 'TELECOM', 'type': 'ACADEMIC', 'campus': campus_bon},
            {'name': 'Service Scolarité Bonabéri', 'code': 'SCO-BON', 'type': 'ADMINISTRATIVE', 'campus': campus_bon},
            
            # Campus Yaoundé
            {'name': 'Département Droit', 'code': 'DROIT', 'type': 'ACADEMIC', 'campus': campus_yde},
            {'name': 'Département Sciences Politiques', 'code': 'SCPO', 'type': 'ACADEMIC', 'campus': campus_yde},
            {'name': 'Service Scolarité Yaoundé', 'code': 'SCO-YDE', 'type': 'ADMINISTRATIVE', 'campus': campus_yde},
            
            # Campus Bafoussam
            {'name': 'Département Agronomie', 'code': 'AGRO', 'type': 'ACADEMIC', 'campus': campus_baf},
            {'name': 'Département Élevage', 'code': 'ELEV', 'type': 'ACADEMIC', 'campus': campus_baf},
            {'name': 'Service Scolarité Bafoussam', 'code': 'SCO-BAF', 'type': 'ADMINISTRATIVE', 'campus': campus_baf},
        ]

        for data in departments_data:
            Department.objects.get_or_create(code=data['code'], defaults=data)
            self.stdout.write(f'  ✓ {data["name"]} ({data["campus"].name})')

    def _seed_users(self):
        self.stdout.write('\n👥 Création des utilisateurs...')

        dsi = Department.objects.get(code='DSI')
        info = Department.objects.get(code='INFO')
        log = Department.objects.get(code='LOG')
        df = Department.objects.get(code='DF')
        drh = Department.objects.get(code='DRH')
        daa = Department.objects.get(code='DAA')

        users_data = [
            # Administrateurs
            {'email': 'admin@iuc.cm', 'first_name': 'Paul', 'last_name': 'Biya', 'matricule': 'IUC001', 'role': 'ADMIN', 'department': dsi, 'phone': '+237 699 01 01 01'},
            {'email': 'dsi@iuc.cm', 'first_name': 'Jean-Pierre', 'last_name': 'Kamga', 'matricule': 'IUC002', 'role': 'ADMIN', 'department': dsi, 'phone': '+237 699 02 02 02'},
            
            # Managers
            {'email': 'directeur.logistique@iuc.cm', 'first_name': 'Marie', 'last_name': 'Ngo Mbock', 'matricule': 'IUC010', 'role': 'MANAGER', 'department': log, 'phone': '+237 677 10 10 10'},
            {'email': 'directeur.finance@iuc.cm', 'first_name': 'André', 'last_name': 'Fotso', 'matricule': 'IUC011', 'role': 'MANAGER', 'department': df, 'phone': '+237 677 11 11 11'},
            {'email': 'directeur.info@iuc.cm', 'first_name': 'Christine', 'last_name': 'Tchinda', 'matricule': 'IUC012', 'role': 'MANAGER', 'department': info, 'phone': '+237 677 12 12 12'},
            {'email': 'drh@iuc.cm', 'first_name': 'Sophie', 'last_name': 'Ekambi', 'matricule': 'IUC013', 'role': 'MANAGER', 'department': drh, 'phone': '+237 677 13 13 13'},
            {'email': 'daa@iuc.cm', 'first_name': 'Pierre', 'last_name': 'Tagne', 'matricule': 'IUC014', 'role': 'MANAGER', 'department': daa, 'phone': '+237 677 14 14 14'},
            
            # Superviseurs
            {'email': 'superviseur.stock@iuc.cm', 'first_name': 'David', 'last_name': 'Eyango', 'matricule': 'IUC020', 'role': 'SUPERVISOR', 'department': log, 'phone': '+237 677 20 20 20'},
            {'email': 'superviseur.it@iuc.cm', 'first_name': 'Esther', 'last_name': 'Mbah', 'matricule': 'IUC021', 'role': 'SUPERVISOR', 'department': dsi, 'phone': '+237 677 21 21 21'},
            
            # Opérateurs
            {'email': 'magasinier1@iuc.cm', 'first_name': 'Joseph', 'last_name': 'Tchouassi', 'matricule': 'IUC030', 'role': 'OPERATOR', 'department': log, 'phone': '+237 655 30 30 30'},
            {'email': 'magasinier2@iuc.cm', 'first_name': 'Alice', 'last_name': 'Moukouri', 'matricule': 'IUC031', 'role': 'OPERATOR', 'department': log, 'phone': '+237 655 31 31 31'},
            {'email': 'technicien.it@iuc.cm', 'first_name': 'François', 'last_name': 'Ndam', 'matricule': 'IUC032', 'role': 'OPERATOR', 'department': dsi, 'phone': '+237 655 32 32 32'},
            {'email': 'comptable@iuc.cm', 'first_name': 'Rose', 'last_name': 'Djoumessi', 'matricule': 'IUC033', 'role': 'OPERATOR', 'department': df, 'phone': '+237 655 33 33 33'},
            
            # Viewers (enseignants, chefs département)
            {'email': 'chef.info@iuc.cm', 'first_name': 'Prof. Samuel', 'last_name': 'Noumsi', 'matricule': 'IUC040', 'role': 'VIEWER', 'department': info, 'phone': '+237 699 40 40 40'},
            {'email': 'chef.gestion@iuc.cm', 'first_name': 'Dr. Yvonne', 'last_name': 'Mbarga', 'matricule': 'IUC041', 'role': 'VIEWER', 'department': Department.objects.get(code='GEST'), 'phone': '+237 699 41 41 41'},
            {'email': 'bibliothecaire@iuc.cm', 'first_name': 'Martine', 'last_name': 'Essomba', 'matricule': 'IUC042', 'role': 'VIEWER', 'department': Department.objects.get(code='BIB'), 'phone': '+237 699 42 42 42'},
            
            # Auditeur
            {'email': 'auditeur@iuc.cm', 'first_name': 'Cabinet', 'last_name': 'Audit Interne', 'matricule': 'IUC050', 'role': 'AUDITOR', 'department': df, 'phone': '+237 677 50 50 50'},
        ]

        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'matricule': data['matricule'],
                    'role': data['role'],
                    'department': data['department'],
                    'phone': data['phone'],
                    'is_active': True,
                    'is_verified': True,
                    'email_verified': True,
                }
            )
            if created:
                user.set_password('IUC@2026!')
                user.save()
                self.stdout.write(f'  ✓ {data["first_name"]} {data["last_name"]} ({data["role"]})')
            else:
                self.stdout.write(f'  → {data["first_name"]} {data["last_name"]} existe déjà')

    def _seed_warehouses(self):
        self.stdout.write('\n🏭 Création des entrepôts...')

        warehouses_data = [
            {'name': 'Entrepôt Central Douala', 'code': 'WH-CENTRAL', 'campus_code': 'CAMPUS-DLA', 'type': 'MAIN', 'capacity': 500},
            {'name': 'Magasin Informatique', 'code': 'WH-INFO', 'campus_code': 'CAMPUS-DLA', 'type': 'SECONDARY', 'capacity': 100},
            {'name': 'Magasin Fournitures', 'code': 'WH-FOURN', 'campus_code': 'CAMPUS-DLA', 'type': 'SECONDARY', 'capacity': 150},
            {'name': 'Entrepôt Bonabéri', 'code': 'WH-BON', 'campus_code': 'CAMPUS-BON', 'type': 'MAIN', 'capacity': 300},
            {'name': 'Magasin Labo Bonabéri', 'code': 'WH-LABO-BON', 'campus_code': 'CAMPUS-BON', 'type': 'SECONDARY', 'capacity': 80},
            {'name': 'Entrepôt Yaoundé', 'code': 'WH-YDE', 'campus_code': 'CAMPUS-YDE', 'type': 'MAIN', 'capacity': 200},
            {'name': 'Entrepôt Bafoussam', 'code': 'WH-BAF', 'campus_code': 'CAMPUS-BAF', 'type': 'MAIN', 'capacity': 150},
        ]

        for data in warehouses_data:
            campus = Campus.objects.get(code=data.pop('campus_code'))
            Warehouse.objects.get_or_create(
                code=data['code'],
                defaults={**data, 'campus': campus}
            )
            self.stdout.write(f'  ✓ {data["name"]} ({campus.name})')

    def _seed_categories(self):
        self.stdout.write('\n📁 Création des catégories...')

        categories_tree = {
            'Informatique': {
                'code': 'CAT-INFO',
                'children': {
                    'Ordinateurs': {'code': 'CAT-ORDI'},
                    'Périphériques': {'code': 'CAT-PERIPH'},
                    'Réseau': {'code': 'CAT-RESEAU'},
                    'Logiciels': {'code': 'CAT-LOGIC'},
                    'Consommables Informatiques': {'code': 'CAT-CONSO-INFO'},
                }
            },
            'Bureautique': {
                'code': 'CAT-BUR',
                'children': {
                    'Fournitures de Bureau': {'code': 'CAT-FOURN-BUR'},
                    'Papeterie': {'code': 'CAT-PAP'},
                    'Mobilier de Bureau': {'code': 'CAT-MOB-BUR'},
                }
            },
            'Laboratoire': {
                'code': 'CAT-LABO',
                'children': {
                    'Équipements Laboratoire': {'code': 'CAT-EQUIP-LAB'},
                    'Produits Chimiques': {'code': 'CAT-CHIMIE'},
                    'Verrerie': {'code': 'CAT-VERRE'},
                }
            },
            'Génie Civil': {
                'code': 'CAT-GC',
                'children': {
                    'Matériaux Construction': {'code': 'CAT-MAT-CONST'},
                    'Outillage': {'code': 'CAT-OUTIL'},
                }
            },
            'Général': {
                'code': 'CAT-GEN',
                'children': {
                    'Mobilier': {'code': 'CAT-MOB'},
                    'Équipements Audiovisuels': {'code': 'CAT-AUDIOV'},
                    'Climatisation': {'code': 'CAT-CLIM'},
                    'Sécurité': {'code': 'CAT-SECU'},
                    'Transport': {'code': 'CAT-TRANSP'},
                }
            },
        }

        self._create_categories(None, categories_tree)

    def _create_categories(self, parent, tree):
        for name, data in tree.items():
            cat, _ = Category.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': name,
                    'parent': parent,
                }
            )
            self.stdout.write(f'  ✓ {name}')
            if 'children' in data:
                self._create_categories(cat, data['children'])

    def _seed_suppliers(self):
        self.stdout.write('\n🚚 Création des fournisseurs...')

        suppliers_data = [
            {'name': 'TechSupply Cameroun', 'code': 'SUP-TECH', 'contact_person': 'M. Kamdem', 'email': 'contact@techsupply.cm', 'phone': '+237 233 45 67 89', 'city': 'Douala', 'category': 'Informatique', 'rating': 5},
            {'name': 'BureauPlus SARL', 'code': 'SUP-BURPLUS', 'contact_person': 'Mme. Ndongo', 'email': 'ventes@bureauplus.cm', 'phone': '+237 233 46 78 90', 'city': 'Douala', 'category': 'Bureautique', 'rating': 4},
            {'name': 'LaboEquip Afrique', 'code': 'SUP-LABO', 'contact_person': 'Dr. Njoya', 'email': 'info@laboequip.cm', 'phone': '+237 233 47 89 01', 'city': 'Yaoundé', 'category': 'Laboratoire', 'rating': 4},
            {'name': 'ConstruMat Cameroon', 'code': 'SUP-CONST', 'contact_person': 'M. Tchinda', 'email': 'commandes@construmat.cm', 'phone': '+237 233 48 90 12', 'city': 'Douala', 'category': 'Matériaux', 'rating': 3},
            {'name': 'Papeterie Moderne', 'code': 'SUP-PAP', 'contact_person': 'Mme. Foning', 'email': 'contact@papeterie-moderne.cm', 'phone': '+237 233 49 01 23', 'city': 'Douala', 'category': 'Papeterie', 'rating': 4},
            {'name': 'Africa Mobilier Pro', 'code': 'SUP-MOB', 'contact_person': 'M. Kuete', 'email': 'ventes@africamobilier.cm', 'phone': '+237 233 50 12 34', 'city': 'Douala', 'category': 'Mobilier', 'rating': 4},
            {'name': 'SécuritéPlus SA', 'code': 'SUP-SECU', 'contact_person': 'M. Ewane', 'email': 'info@securiteplus.cm', 'phone': '+237 233 51 23 45', 'city': 'Douala', 'category': 'Sécurité', 'rating': 5},
            {'name': 'AutoParts Cameroun', 'code': 'SUP-AUTO', 'contact_person': 'M. Simo', 'email': 'pieces@autoparts.cm', 'phone': '+237 233 52 34 56', 'city': 'Douala', 'category': 'Transport', 'rating': 3},
            {'name': 'ClimTech Services', 'code': 'SUP-CLIM', 'contact_person': 'M. Nguema', 'email': 'service@climtech.cm', 'phone': '+237 233 53 45 67', 'city': 'Yaoundé', 'category': 'Climatisation', 'rating': 4},
            {'name': 'AudioVisuel Pro', 'code': 'SUP-AV', 'contact_person': 'Mme. Biloa', 'email': 'ventes@avpro.cm', 'phone': '+237 233 54 56 78', 'city': 'Douala', 'category': 'Audiovisuel', 'rating': 4},
        ]

        for data in suppliers_data:
            Supplier.objects.get_or_create(code=data['code'], defaults=data)
            self.stdout.write(f'  ✓ {data["name"]}')

    def _seed_products(self):
        self.stdout.write('\n📦 Création des produits...')
        
        products_data = [
            # Informatique - Ordinateurs
            {'name': 'Ordinateur Portable Dell Latitude 5540', 'reference': 'DELL-LAT-5540', 'sku': 'INFO-ORD-001', 'category_code': 'CAT-ORDI', 'brand': 'Dell', 'unit_price': 450000, 'min_stock': 10, 'max_stock': 50, 'unit': 'PIECE'},
            {'name': 'Ordinateur de Bureau HP EliteDesk 800', 'reference': 'HP-ELITE-800', 'sku': 'INFO-ORD-002', 'category_code': 'CAT-ORDI', 'brand': 'HP', 'unit_price': 380000, 'min_stock': 15, 'max_stock': 60, 'unit': 'PIECE'},
            {'name': 'iMac 24" M3', 'reference': 'APPLE-IMAC-24', 'sku': 'INFO-ORD-003', 'category_code': 'CAT-ORDI', 'brand': 'Apple', 'unit_price': 850000, 'min_stock': 3, 'max_stock': 10, 'unit': 'PIECE'},
            {'name': 'Ordinateur Portable Lenovo ThinkPad X1', 'reference': 'LEN-X1-CARBON', 'sku': 'INFO-ORD-004', 'category_code': 'CAT-ORDI', 'brand': 'Lenovo', 'unit_price': 520000, 'min_stock': 8, 'max_stock': 30, 'unit': 'PIECE'},
            
            # Informatique - Périphériques
            {'name': 'Imprimante Multifonction HP LaserJet Pro', 'reference': 'HP-LJ-MFP4101', 'sku': 'INFO-PER-001', 'category_code': 'CAT-PERIPH', 'brand': 'HP', 'unit_price': 180000, 'min_stock': 5, 'max_stock': 20, 'unit': 'PIECE'},
            {'name': 'Projecteur Epson EB-X51', 'reference': 'EPS-EBX51', 'sku': 'INFO-PER-002', 'category_code': 'CAT-PERIPH', 'brand': 'Epson', 'unit_price': 300000, 'min_stock': 3, 'max_stock': 15, 'unit': 'PIECE'},
            {'name': 'Écran LED 24" Dell', 'reference': 'DELL-P2422H', 'sku': 'INFO-PER-003', 'category_code': 'CAT-PERIPH', 'brand': 'Dell', 'unit_price': 120000, 'min_stock': 10, 'max_stock': 40, 'unit': 'PIECE'},
            {'name': 'Clavier + Souris Sans Fil Logitech', 'reference': 'LOG-MK270', 'sku': 'INFO-PER-004', 'category_code': 'CAT-PERIPH', 'brand': 'Logitech', 'unit_price': 15000, 'min_stock': 20, 'max_stock': 100, 'unit': 'SET'},
            
            # Informatique - Réseau
            {'name': 'Switch Cisco 24 Ports Gigabit', 'reference': 'CISCO-SG350-24', 'sku': 'INFO-RES-001', 'category_code': 'CAT-RESEAU', 'brand': 'Cisco', 'unit_price': 250000, 'min_stock': 2, 'max_stock': 10, 'unit': 'PIECE'},
            {'name': 'Point d\'Accès WiFi Ubiquiti UniFi 6', 'reference': 'UB-U6-LR', 'sku': 'INFO-RES-002', 'category_code': 'CAT-RESEAU', 'brand': 'Ubiquiti', 'unit_price': 80000, 'min_stock': 5, 'max_stock': 30, 'unit': 'PIECE'},
            {'name': 'Câble RJ45 Cat6 (rouleau 305m)', 'reference': 'CABLE-CAT6-305', 'sku': 'INFO-RES-003', 'category_code': 'CAT-RESEAU', 'brand': 'Generic', 'unit_price': 45000, 'min_stock': 3, 'max_stock': 15, 'unit': 'PIECE'},
            
            # Informatique - Consommables
            {'name': 'Cartouche d\'encre HP 305A Noire', 'reference': 'HP-305A-BK', 'sku': 'INFO-CONS-001', 'category_code': 'CAT-CONSO-INFO', 'brand': 'HP', 'unit_price': 35000, 'min_stock': 10, 'max_stock': 50, 'unit': 'PIECE'},
            {'name': 'Clé USB 64 Go SanDisk', 'reference': 'SANDISK-64GB', 'sku': 'INFO-CONS-002', 'category_code': 'CAT-CONSO-INFO', 'brand': 'SanDisk', 'unit_price': 5000, 'min_stock': 30, 'max_stock': 200, 'unit': 'PIECE'},
            {'name': 'Disque Dur Externe 2 To Seagate', 'reference': 'SEAGATE-2TB', 'sku': 'INFO-CONS-003', 'category_code': 'CAT-CONSO-INFO', 'brand': 'Seagate', 'unit_price': 35000, 'min_stock': 5, 'max_stock': 30, 'unit': 'PIECE'},
            
            # Bureautique - Papeterie
            {'name': 'Papier A4 80g (ramette 500 feuilles)', 'reference': 'PAP-A4-80', 'sku': 'BUR-PAP-001', 'category_code': 'CAT-PAP', 'brand': 'Double A', 'unit_price': 2500, 'min_stock': 100, 'max_stock': 1000, 'unit': 'PIECE'},
            {'name': 'Stylo Bille Bic Cristal (boîte 50)', 'reference': 'BIC-CRISTAL-50', 'sku': 'BUR-PAP-002', 'category_code': 'CAT-PAP', 'brand': 'Bic', 'unit_price': 3000, 'min_stock': 20, 'max_stock': 100, 'unit': 'BOX'},
            {'name': 'Marqueur Tableau Blanc (pack 4)', 'reference': 'MARK-TB-P4', 'sku': 'BUR-PAP-003', 'category_code': 'CAT-PAP', 'brand': 'Expo', 'unit_price': 2000, 'min_stock': 15, 'max_stock': 80, 'unit': 'PACK'},
            {'name': 'Cahier de Cours 300 Pages', 'reference': 'CAH-300P', 'sku': 'BUR-PAP-004', 'category_code': 'CAT-PAP', 'brand': 'Generic', 'unit_price': 1500, 'min_stock': 50, 'max_stock': 500, 'unit': 'PIECE'},
            
            # Bureautique - Mobilier
            {'name': 'Bureau Enseignant avec Rangement', 'reference': 'BUR-ENS-001', 'sku': 'BUR-MOB-001', 'category_code': 'CAT-MOB-BUR', 'brand': 'Africa Mobilier', 'unit_price': 120000, 'min_stock': 5, 'max_stock': 30, 'unit': 'PIECE'},
            {'name': 'Chaise Étudiant', 'reference': 'CHAISE-ETU-001', 'sku': 'BUR-MOB-002', 'category_code': 'CAT-MOB-BUR', 'brand': 'Africa Mobilier', 'unit_price': 15000, 'min_stock': 50, 'max_stock': 500, 'unit': 'PIECE'},
            {'name': 'Table de Réunion 8 Places', 'reference': 'TABLE-REU-8', 'sku': 'BUR-MOB-003', 'category_code': 'CAT-MOB-BUR', 'brand': 'Africa Mobilier', 'unit_price': 200000, 'min_stock': 2, 'max_stock': 10, 'unit': 'PIECE'},
            {'name': 'Armoire de Rangement Métallique', 'reference': 'ARM-MET-001', 'sku': 'BUR-MOB-004', 'category_code': 'CAT-MOB-BUR', 'brand': 'Generic', 'unit_price': 85000, 'min_stock': 3, 'max_stock': 20, 'unit': 'PIECE'},
            
            # Laboratoire
            {'name': 'Microscope Binoculaire Olympus CX23', 'reference': 'OLY-CX23', 'sku': 'LAB-EQU-001', 'category_code': 'CAT-EQUIP-LAB', 'brand': 'Olympus', 'unit_price': 500000, 'min_stock': 2, 'max_stock': 10, 'unit': 'PIECE'},
            {'name': 'Balance de Précision 0.001g', 'reference': 'BAL-PREC-001', 'sku': 'LAB-EQU-002', 'category_code': 'CAT-EQUIP-LAB', 'brand': 'Mettler Toledo', 'unit_price': 350000, 'min_stock': 2, 'max_stock': 8, 'unit': 'PIECE'},
            {'name': 'Bécher 500ml Pyrex', 'reference': 'PYR-BECH-500', 'sku': 'LAB-VER-001', 'category_code': 'CAT-VERRE', 'brand': 'Pyrex', 'unit_price': 8000, 'min_stock': 20, 'max_stock': 100, 'unit': 'PIECE'},
            {'name': 'Acide Sulfurique 95% (1L)', 'reference': 'CHIM-H2SO4-1L', 'sku': 'LAB-CHIM-001', 'category_code': 'CAT-CHIMIE', 'brand': 'Merck', 'unit_price': 15000, 'min_stock': 5, 'max_stock': 30, 'unit': 'PIECE'},
            
            # Général - Audiovisuel
            {'name': 'Tableau Blanc Interactif SMART Board', 'reference': 'SMART-SB680', 'sku': 'GEN-AV-001', 'category_code': 'CAT-AUDIOV', 'brand': 'SMART', 'unit_price': 750000, 'min_stock': 2, 'max_stock': 8, 'unit': 'PIECE'},
            {'name': 'Système de Sonorisation Salle 100W', 'reference': 'SONO-100W', 'sku': 'GEN-AV-002', 'category_code': 'CAT-AUDIOV', 'brand': 'Yamaha', 'unit_price': 350000, 'min_stock': 1, 'max_stock': 5, 'unit': 'PIECE'},
            
            # Général - Climatisation
            {'name': 'Climatiseur Split 18000 BTU', 'reference': 'CLIM-SPLIT-18K', 'sku': 'GEN-CLIM-001', 'category_code': 'CAT-CLIM', 'brand': 'Samsung', 'unit_price': 250000, 'min_stock': 3, 'max_stock': 15, 'unit': 'PIECE'},
            
            # Général - Sécurité
            {'name': 'Extincteur CO2 5kg', 'reference': 'EXT-CO2-5', 'sku': 'GEN-SEC-001', 'category_code': 'CAT-SECU', 'brand': 'Generic', 'unit_price': 45000, 'min_stock': 10, 'max_stock': 50, 'unit': 'PIECE'},
            
            # Génie Civil
            {'name': 'Ciment CPJ35 (sac 50kg)', 'reference': 'CIM-CPJ35-50', 'sku': 'GC-MAT-001', 'category_code': 'CAT-MAT-CONST', 'brand': 'Cimencam', 'unit_price': 5500, 'min_stock': 20, 'max_stock': 200, 'unit': 'PIECE'},
            {'name': 'Fer à Béton Ø10 (barre 12m)', 'reference': 'FER-BET-10', 'sku': 'GC-MAT-002', 'category_code': 'CAT-MAT-CONST', 'brand': 'Generic', 'unit_price': 3500, 'min_stock': 50, 'max_stock': 500, 'unit': 'PIECE'},
        ]

        # Récupérer les fournisseurs pour assignation
        suppliers = {
            'Informatique': Supplier.objects.get(code='SUP-TECH'),
            'Bureautique': Supplier.objects.get(code='SUP-BURPLUS'),
            'Laboratoire': Supplier.objects.get(code='SUP-LABO'),
            'Papeterie': Supplier.objects.get(code='SUP-PAP'),
            'Mobilier': Supplier.objects.get(code='SUP-MOB'),
            'Général': Supplier.objects.get(code='SUP-AV'),
            'Sécurité': Supplier.objects.get(code='SUP-SECU'),
            'Génie Civil': Supplier.objects.get(code='SUP-CONST'),
            'Climatisation': Supplier.objects.get(code='SUP-CLIM'),
        }

        for data in products_data:
            category = Category.objects.get(code=data.pop('category_code'))
            
            # Déterminer le fournisseur
            supplier = None
            for key, sup in suppliers.items():
                if key.lower() in category.name.lower() or key.lower() in data.get('brand', '').lower():
                    supplier = sup
                    break
            if not supplier:
                supplier = Supplier.objects.get(code='SUP-TECH')
            
            product, created = Product.objects.get_or_create(
                reference=data['reference'],
                defaults={
                    **data,
                    'category': category,
                    'supplier': supplier,
                    'status': 'ACTIVE',
                }
            )
            if created:
                self.stdout.write(f'  ✓ {data["name"]} ({data["reference"]})')

    def _seed_stocks(self):
        self.stdout.write('\n📊 Création des stocks...')
        
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        count = 0
        for product in products:
            # Assigner 2-3 entrepôts par produit
            assigned_warehouses = random.sample(list(warehouses), min(random.randint(2, 4), len(warehouses)))
            
            for warehouse in assigned_warehouses:
                quantity = random.randint(
                    max(0, product.min_stock - 5),
                    product.max_stock + 10
                )
                
                Stock.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': quantity,
                        'reserved_quantity': random.randint(0, max(0, quantity // 4)),
                        'unit_price': product.unit_price,
                        'location': f'R{random.randint(1,10)}-E{random.randint(1,5)}',
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ {count} entrées de stock créées')

    def _seed_movements(self):
        self.stdout.write('\n🔄 Création des mouvements...')
        
        stocks = Stock.objects.all()
        users = User.objects.filter(role__in=['OPERATOR', 'MANAGER', 'SUPERVISOR'])
        users_list = list(users) if users.exists() else [User.objects.first()]
        
        if not users_list:
            self.stdout.write('  ⚠ Aucun utilisateur trouvé pour les mouvements')
            return
        
        count = 0
        for stock in stocks[:50]:  # Limiter à 50 stocks
            # Créer 2-5 mouvements par stock
            for _ in range(random.randint(2, 5)):
                movement_type = random.choice(['ENTRY', 'OUTPUT'])
                quantity = random.randint(1, 20)
                
                StockMovement.objects.create(
                    movement_type=movement_type,
                    reason='PURCHASE' if movement_type == 'ENTRY' else 'INTERNAL_USE',
                    stock=stock,
                    quantity=quantity,
                    unit_price=stock.unit_price,
                    total_price=Decimal(quantity) * stock.unit_price,
                    performed_by=random.choice(users_list),
                    is_validated=True,
                    validated_at=timezone.now() - timedelta(days=random.randint(0, 90)),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 180)),
                )
                count += 1
        
        self.stdout.write(f'  ✓ {count} mouvements créés')

    def _seed_purchase_orders(self):
        self.stdout.write('\n📋 Création des commandes...')
        
        suppliers = Supplier.objects.all()
        products = list(Product.objects.all())
        users = User.objects.filter(role__in=['MANAGER', 'SUPERVISOR', 'ADMIN'])
        users_list = list(users) if users.exists() else [User.objects.first()]
        
        if not users_list or not suppliers.exists():
            self.stdout.write('  ⚠ Données manquantes pour les commandes')
            return
        
        statuses = ['DRAFT', 'PENDING', 'APPROVED', 'ORDERED', 'RECEIVED']
        
        count = 0
        for i in range(15):
            supplier = random.choice(list(suppliers))
            status = random.choice(statuses)
            
            order = PurchaseOrder.objects.create(
                supplier=supplier,
                status=status,
                order_date=timezone.now().date() - timedelta(days=random.randint(0, 60)),
                expected_delivery_date=timezone.now().date() + timedelta(days=random.randint(5, 30)),
                requested_by=random.choice(users_list),
                notes=f'Commande #{i+1} - IUC',
            )
            
            # Ajouter 2-4 lignes
            order_products = random.sample(products, min(random.randint(2, 4), len(products)))
            for product in order_products:
                qty = random.randint(5, 30)
                line = PurchaseOrderLine.objects.create(
                    purchase_order=order,
                    product=product,
                    quantity=qty,
                    unit_price=product.unit_price,
                )
                if status == 'RECEIVED':
                    line.received_quantity = qty
                    line.save()
            
            order.total_amount = sum(line.total_price for line in order.lines.all())
            order.save()
            count += 1
        
        self.stdout.write(f'  ✓ {count} commandes créées')

    def _seed_inventories(self):
        self.stdout.write('\n📋 Création des inventaires...')
        
        warehouses = Warehouse.objects.all()[:3]
        users = User.objects.filter(role__in=['MANAGER', 'SUPERVISOR'])
        users_list = list(users) if users.exists() else [User.objects.first()]
        
        if not users_list:
            self.stdout.write('  ⚠ Aucun utilisateur trouvé pour les inventaires')
            return
        
        count = 0
        for warehouse in warehouses:
            inventory = Inventory.objects.create(
                type='FULL',
                status='COMPLETED',
                warehouse=warehouse,
                start_date=timezone.now() - timedelta(days=random.randint(30, 90)),
                end_date=timezone.now() - timedelta(days=random.randint(25, 85)),
                supervisor=random.choice(users_list),
                description=f'Inventaire trimestriel {warehouse.name}',
            )
            
            # Ajouter les lignes
            stocks = Stock.objects.filter(warehouse=warehouse, is_deleted=False)[:20]
            for stock in stocks:
                diff = random.randint(-5, 5)
                InventoryLine.objects.create(
                    inventory=inventory,
                    product=stock.product,
                    expected_quantity=stock.quantity,
                    counted_quantity=stock.quantity + diff,
                    unit_price=stock.unit_price,
                )
            
            # Mettre à jour les compteurs
            lines = inventory.lines.all()
            inventory.expected_items = lines.count()
            inventory.counted_items = lines.filter(counted_quantity__isnull=False).count()
            inventory.differences = sum((l.counted_quantity or 0) - l.expected_quantity for l in lines if l.counted_quantity is not None)
            inventory.total_value_expected = sum(l.expected_quantity * l.unit_price for l in lines)
            inventory.total_value_counted = sum((l.counted_quantity or 0) * l.unit_price for l in lines if l.counted_quantity is not None)
            inventory.value_difference = float(inventory.total_value_counted) - float(inventory.total_value_expected)
            inventory.save()
            count += 1
        
        self.stdout.write(f'  ✓ {count} inventaires créés')

    def _seed_qr_codes(self):
        self.stdout.write('\n📱 Création des QR Codes...')
        
        products = Product.objects.all()[:30]
        count = 0
        
        import json
        for product in products:
            qr_data = json.dumps({
                'type': 'product',
                'id': str(product.id),
                'reference': product.reference,
                'name': product.name,
            })
            
            QRCode.objects.get_or_create(
                product=product,
                defaults={
                    'code': qr_data,
                    'is_active': True,
                }
            )
            count += 1
        
        self.stdout.write(f'  ✓ {count} QR Codes créés')

    def _print_summary(self):
        self.stdout.write('\n📊 RÉSUMÉ DU SEEDING :')
        self.stdout.write(f'  • Campus       : {Campus.objects.count()}')
        self.stdout.write(f'  • Départements : {Department.objects.count()}')
        self.stdout.write(f'  • Utilisateurs : {User.objects.count()}')
        self.stdout.write(f'  • Entrepôts    : {Warehouse.objects.count()}')
        self.stdout.write(f'  • Catégories   : {Category.objects.count()}')
        self.stdout.write(f'  • Fournisseurs : {Supplier.objects.count()}')
        self.stdout.write(f'  • Produits     : {Product.objects.count()}')
        self.stdout.write(f'  • Stocks       : {Stock.objects.count()}')
        self.stdout.write(f'  • Mouvements   : {StockMovement.objects.count()}')
        self.stdout.write(f'  • Commandes    : {PurchaseOrder.objects.count()}')
        self.stdout.write(f'  • Inventaires  : {Inventory.objects.count()}')
        self.stdout.write(f'  • QR Codes     : {QRCode.objects.count()}')
        self.stdout.write(f'')
        self.stdout.write(self.style.SUCCESS('🔑 Comptes de connexion :'))
        self.stdout.write(f'  Admin      : admin@iuc.cm / IUC@2026!')
        self.stdout.write(f'  Manager    : directeur.logistique@iuc.cm / IUC@2026!')
        self.stdout.write(f'  Opérateur  : magasinier1@iuc.cm / IUC@2026!')
        self.stdout.write(f'  Viewer     : chef.info@iuc.cm / IUC@2026!')