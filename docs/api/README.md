# Documentation API - IUC Inventory System

## Base URL
```
https://api.iuc.cm/api/v1/
```

## Authentification

### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@iuc.cm",
  "password": "your-password"
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 1800,
    "token_type": "Bearer",
    "user": { ... }
  }
}
```

### Header d'authentification
```http
Authorization: Bearer <access_token>
```



## Endpoints

### Authentification

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| POST | `/auth/login/` | Connexion | Public |
| POST | `/auth/register/` | Inscription | Public |
| POST | `/auth/refresh/` | Rafraîchir token | Public |
| POST | `/auth/logout/` | Déconnexion | Auth |
| GET | `/auth/profile/` | Profil utilisateur | Auth |
| POST | `/auth/change-password/` | Changer mot de passe | Auth |

### Produits

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/products/` | Liste produits | Operator+ |
| POST | `/products/` | Créer produit | Manager+ |
| GET | `/products/{id}/` | Détail produit | Operator+ |
| PATCH | `/products/{id}/` | Modifier produit | Manager+ |
| DELETE | `/products/{id}/` | Supprimer produit | Manager+ |
| GET | `/products/low-stock/` | Produits en alerte | Manager+ |
| POST | `/products/search/` | Recherche avancée | Operator+ |

### Catégories

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/categories/` | Liste catégories | Operator+ |
| POST | `/categories/` | Créer catégorie | Manager+ |
| GET | `/categories/{id}/` | Détail catégorie | Operator+ |
| PATCH | `/categories/{id}/` | Modifier catégorie | Manager+ |
| DELETE | `/categories/{id}/` | Supprimer catégorie | Manager+ |

### Stocks

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/stocks/` | Vue d'ensemble stocks | Operator+ |
| GET | `/stocks/{id}/` | Détail stock | Operator+ |
| GET | `/movements/` | Historique mouvements | Operator+ |
| POST | `/movements/` | Créer mouvement | Operator+ |
| POST | `/movements/{id}/validate/` | Valider mouvement | Manager+ |

### Entrées/Sorties/Transferts

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET/POST | `/stock-entries/` | Entrées de stock | Operator+/Manager+ |
| GET/POST | `/stock-outputs/` | Sorties de stock | Operator+/Manager+ |
| GET/POST | `/transfers/` | Transferts | Operator+/Manager+ |

### Inventaires

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/inventories/` | Liste inventaires | Operator+ |
| POST | `/inventories/` | Créer inventaire | Manager+ |
| GET | `/inventories/{id}/` | Détail inventaire | Operator+ |
| POST | `/inventories/{id}/start/` | Démarrer inventaire | Manager+ |
| POST | `/inventories/{id}/validate/` | Valider inventaire | Manager+ |
| PATCH | `/inventories/{id}/lines/{lid}/` | Mettre à jour ligne | Operator+ |

### Rapports

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| POST | `/reports/generate/` | Générer rapport | Manager+ |
| GET | `/reports/history/` | Historique rapports | Manager+ |

### QR Codes

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| POST | `/products/{id}/qr/generate/` | Générer QR code | Manager+ |
| POST | `/products/{id}/barcode/generate/` | Générer code-barres | Manager+ |
| GET | `/products/{id}/codes/` | Voir les codes | Operator+ |
| POST | `/qr/scan/` | Scanner QR code | Operator+ |
| POST | `/qr/bulk-print/` | Impression en masse | Manager+ |

### Notifications

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/notifications/` | Mes notifications | Operator+ |
| POST | `/notifications/{id}/read/` | Marquer lue | Operator+ |
| POST | `/notifications/read-all/` | Tout marquer lu | Operator+ |

### RBAC

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET/POST | `/rbac/roles/` | Rôles | Manager+/Admin |
| GET | `/rbac/permissions/` | Permissions | Manager+ |
| GET | `/rbac/my-permissions/` | Mes permissions | Auth |

### Dashboard

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/dashboard/` | Données tableau de bord | Operator+ |



## Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Non trouvé |
| 409 | Conflit |
| 429 | Trop de requêtes |
| 500 | Erreur serveur |



## Pagination

Toutes les listes sont paginées :
```json
{
  "success": true,
  "data": {
    "count": 150,
    "next": "http://api.iuc.cm/api/v1/products/?page=2",
    "previous": null,
    "results": [...]
  }
}
```

Paramètres : `?page=2&page_size=50` (max 100)