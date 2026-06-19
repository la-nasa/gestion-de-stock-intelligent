# Architecture - IUC Inventory System

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx Reverse Proxy                     │
│                    (SSL Termination, LB)                     │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐    ┌──────────▼──────────┐    ┌───────▼───────┐
│   Frontend    │    │     Backend API      │    │  ML Service   │
│   Next.js 15  │    │     Django 5         │    │   FastAPI     │
│   React 19    │    │     DRF + Ninja      │    │               │
└───────────────┘    └──────────┬──────────┘    └───────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐    ┌──────────▼──────────┐    ┌───────▼───────┐
│  PostgreSQL   │    │       Redis         │    │   RabbitMQ    │
│     16        │    │        7            │    │      3        │
└───────────────┘    └─────────────────────┘    └───────────────┘
```

## Stack Technique

| Composant | Technologie | Version |
|-----------|------------|---------|
| Backend | Django + DRF | 5.0 |
| API Alternative | Django Ninja | 1.1 |
| Frontend | Next.js + React | 15 / 19 |
| Base de données | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Message Queue | RabbitMQ | 3 |
| Object Storage | MinIO | Latest |
| ML Service | FastAPI | 0.109 |
| WebSocket | Django Channels | 4.0 |
| Reverse Proxy | Nginx | Alpine |
| Monitoring | Prometheus + Grafana | Latest |
| Container | Docker + Compose | Latest |

## Modules

### Backend (24 apps Django)
- accounts - Gestion utilisateurs
- roles - RBAC
- products - Produits et catégories
- suppliers - Fournisseurs
- warehouses - Entrepôts
- departments - Départements
- campuses - Campus
- stock_movements - Mouvements de stock
- stock_entries - Entrées
- stock_outputs - Sorties
- transfers - Transferts
- purchase_orders - Commandes
- inventories - Inventaires
- requests - Demandes internes
- notifications - Notifications
- audit_logs - Logs d'audit
- attachments - Pièces jointes
- maintenance - Maintenance
- qr_codes - QR Codes
- barcodes - Codes-barres
- dashboard - Tableau de bord
- analytics - Analytiques
- reports - Rapports
- settings - Paramètres

### Frontend
- Dashboard avec KPIs
- Gestion CRUD produits
- Interface stocks
- Rapports multi-formats
- QR Codes
- Chatbot IA
- Notifications temps réel

### ML Service
- Prévisions (Prophet, XGBoost, LSTM)
- Détection d'anomalies (Isolation Forest, AutoEncoder)
- OCR Factures
- Chatbot RAG

## Flux de données

### Entrée de stock
```
1. Utilisateur crée une entrée
2. StockEntry + StockEntryLine créés
3. Validation → StockMovement créé
4. Stock mis à jour
5. Notification envoyée
6. WebSocket broadcast
```

### Inventaire
```
1. Création inventaire → génération lignes depuis Stock
2. Comptage → InventoryLine.counted_quantity
3. Validation → mise à jour Stock
4. Écarts calculés automatiquement
```

## Sécurité

- JWT avec rotation de tokens
- RBAC (6 rôles, 30+ permissions)
- Rate limiting par IP
- Security headers (CSP, HSTS, XSS)
- Brute force protection (django-axes)
- Audit trail complet
- API Key pour ML Service

## Déploiement

- Docker multi-services
- Nginx reverse proxy
- SSL/TLS avec Let's Encrypt
- Backup automatique quotidien
- Monitoring Prometheus + Grafana
- CI/CD GitHub Actions