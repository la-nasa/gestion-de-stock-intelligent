"""
Commande Django pour initialiser les rôles et permissions par défaut.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.roles.models import Role, Permission, RolePermission
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Initialise les rôles et permissions par défaut'
    
    # Définition des rôles système
    SYSTEM_ROLES = [
        {
            'name': 'Administrateur',
            'code': 'ADMIN',
            'description': 'Accès complet à toutes les fonctionnalités du système.',
            'level': 100,
            'is_system': True,
        },
        {
            'name': 'Gestionnaire',
            'code': 'MANAGER',
            'description': 'Gestion des opérations courantes, validation des mouvements.',
            'level': 80,
            'is_system': True,
        },
        {
            'name': 'Superviseur',
            'code': 'SUPERVISOR',
            'description': 'Supervision des stocks, inventaires, et rapports.',
            'level': 60,
            'is_system': True,
        },
        {
            'name': 'Opérateur',
            'code': 'OPERATOR',
            'description': 'Opérations de base : entrées, sorties, mouvements de stock.',
            'level': 40,
            'is_system': True,
        },
        {
            'name': 'Lecteur',
            'code': 'VIEWER',
            'description': 'Consultation uniquement, pas de modification.',
            'level': 20,
            'is_system': True,
        },
        {
            'name': 'Auditeur',
            'code': 'AUDITOR',
            'description': 'Consultation des logs et rapports d\'audit.',
            'level': 30,
            'is_system': True,
        },
    ]
    
    # Définition des permissions par module
    PERMISSIONS = {
        'products': [
            ('products.view_product', 'Voir les produits', 'GLOBAL'),
            ('products.create_product', 'Créer un produit', 'GLOBAL'),
            ('products.edit_product', 'Modifier un produit', 'GLOBAL'),
            ('products.delete_product', 'Supprimer un produit', 'GLOBAL'),
            ('products.view_cost', 'Voir le coût des produits', 'GLOBAL'),
        ],
        'stock': [
            ('stock.view_stock', 'Voir le stock', 'GLOBAL'),
            ('stock.add_stock', 'Ajouter du stock', 'WAREHOUSE'),
            ('stock.remove_stock', 'Retirer du stock', 'WAREHOUSE'),
            ('stock.transfer_stock', 'Transférer du stock', 'WAREHOUSE'),
            ('stock.adjust_stock', 'Ajuster le stock', 'WAREHOUSE'),
        ],
        'orders': [
            ('orders.view_orders', 'Voir les commandes', 'DEPARTMENT'),
            ('orders.create_order', 'Créer une commande', 'DEPARTMENT'),
            ('orders.approve_order', 'Approuver une commande', 'DEPARTMENT'),
            ('orders.cancel_order', 'Annuler une commande', 'DEPARTMENT'),
        ],
        'inventory': [
            ('inventory.view', 'Voir les inventaires', 'WAREHOUSE'),
            ('inventory.create', 'Créer un inventaire', 'WAREHOUSE'),
            ('inventory.participate', 'Participer à un inventaire', 'WAREHOUSE'),
            ('inventory.validate', 'Valider un inventaire', 'WAREHOUSE'),
        ],
        'users': [
            ('users.view', 'Voir les utilisateurs', 'GLOBAL'),
            ('users.create', 'Créer un utilisateur', 'GLOBAL'),
            ('users.edit', 'Modifier un utilisateur', 'GLOBAL'),
            ('users.deactivate', 'Désactiver un utilisateur', 'GLOBAL'),
        ],
        'reports': [
            ('reports.view', 'Voir les rapports', 'DEPARTMENT'),
            ('reports.export', 'Exporter les rapports', 'DEPARTMENT'),
            ('reports.schedule', 'Planifier des rapports', 'DEPARTMENT'),
        ],
        'settings': [
            ('settings.view', 'Voir les paramètres', 'GLOBAL'),
            ('settings.edit', 'Modifier les paramètres', 'GLOBAL'),
        ],
        'dashboard': [
            ('dashboard.view', 'Voir le tableau de bord', 'DEPARTMENT'),
            ('dashboard.export', 'Exporter le tableau de bord', 'DEPARTMENT'),
        ],
        'notifications': [
            ('notifications.view', 'Voir les notifications', 'PERSONAL'),
            ('notifications.send', 'Envoyer des notifications', 'DEPARTMENT'),
        ],
        'audit': [
            ('audit.view', 'Voir les logs d\'audit', 'GLOBAL'),
            ('audit.export', 'Exporter les logs d\'audit', 'GLOBAL'),
        ],
    }
    
    # Assignation des permissions par rôle
    ROLE_PERMISSIONS = {
        'ADMIN': '*',  # Toutes les permissions
        'MANAGER': [
            'products.view_product', 'products.create_product', 'products.edit_product', 'products.view_cost',
            'stock.view_stock', 'stock.add_stock', 'stock.remove_stock', 'stock.transfer_stock', 'stock.adjust_stock',
            'orders.view_orders', 'orders.create_order', 'orders.approve_order',
            'inventory.view', 'inventory.create', 'inventory.participate', 'inventory.validate',
            'users.view',
            'reports.view', 'reports.export',
            'settings.view',
            'dashboard.view', 'dashboard.export',
            'notifications.view', 'notifications.send',
            'audit.view',
        ],
        'SUPERVISOR': [
            'products.view_product', 'products.view_cost',
            'stock.view_stock', 'stock.adjust_stock',
            'orders.view_orders', 'orders.create_order',
            'inventory.view', 'inventory.create', 'inventory.participate', 'inventory.validate',
            'users.view',
            'reports.view', 'reports.export',
            'dashboard.view',
            'notifications.view',
        ],
        'OPERATOR': [
            'products.view_product',
            'stock.view_stock', 'stock.add_stock', 'stock.remove_stock',
            'orders.view_orders', 'orders.create_order',
            'inventory.view', 'inventory.participate',
            'dashboard.view',
            'notifications.view',
        ],
        'VIEWER': [
            'products.view_product',
            'stock.view_stock',
            'orders.view_orders',
            'dashboard.view',
            'notifications.view',
        ],
        'AUDITOR': [
            'products.view_product',
            'stock.view_stock',
            'orders.view_orders',
            'reports.view', 'reports.export',
            'audit.view', 'audit.export',
            'dashboard.view',
            'notifications.view',
        ],
    }
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initialisation des rôles et permissions...'))
        
        # 1. Créer les rôles système
        self.stdout.write('Création des rôles système...')
        roles = {}
        for role_data in self.SYSTEM_ROLES:
            role, created = Role.objects.update_or_create(
                code=role_data['code'],
                defaults=role_data
            )
            roles[role.code] = role
            status = '✓' if created else '↻'
            self.stdout.write(f'  {status} {role.name} ({role.code})')
        
        # 2. Créer les permissions
        self.stdout.write('\nCréation des permissions...')
        permissions = {}
        for module, perms in self.PERMISSIONS.items():
            for code, name, scope in perms:
                perm, created = Permission.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'module': module,
                        'scope': scope,
                    }
                )
                permissions[code] = perm
                status = '+' if created else '·'
                self.stdout.write(f'  {status} {code}')
        
        # 3. Assigner les permissions aux rôles
        self.stdout.write('\nAssignation des permissions...')
        for role_code, perm_list in self.ROLE_PERMISSIONS.items():
            role = roles.get(role_code)
            if not role:
                continue
            
            if perm_list == '*':
                # Toutes les permissions pour ADMIN
                all_perms = list(permissions.values())
                RolePermission.objects.filter(role=role).delete()
                for perm in all_perms:
                    RolePermission.objects.get_or_create(role=role, permission=perm)
                self.stdout.write(f'  ✓ {role.name}: TOUTES ({len(all_perms)} permissions)')
            else:
                # Permissions spécifiques
                # Supprimer les permissions non listées
                RolePermission.objects.filter(role=role).exclude(
                    permission__code__in=perm_list
                ).delete()
                
                # Ajouter les permissions listées
                count = 0
                for code in perm_list:
                    perm = permissions.get(code)
                    if perm:
                        _, created = RolePermission.objects.get_or_create(
                            role=role, permission=perm
                        )
                        if created:
                            count += 1
                
                self.stdout.write(f'  ✓ {role.name}: {len(perm_list)} permissions ({count} nouvelles)')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Initialisation terminée !'))
