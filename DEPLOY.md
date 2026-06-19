# 🚀 Guide de Déploiement Rapide - IUC Inventory System

## Architecture Gratuite

| Service | Plateforme | URL |
|---------|-----------|-----|
| Frontend (Next.js) | **Vercel** | https://iuc-inventory.vercel.app |
| Backend (Django) | **Render** | https://iuc-api.onrender.com |
| ML Service (FastAPI) | **Railway** | https://iuc-ml.up.railway.app |
| Database (PostgreSQL) | **Supabase** | (interne) |
| Redis | **Render Redis** | (interne) |

## Déploiement Rapide

### 1. Frontend (Vercel)
```bash
cd frontend
npm i -g vercel
vercel --prod
```

### 2. Backend (Render)
- Créer un compte sur https://render.com
- Connecter le repo GitHub
- Déployer le dossier `backend/`

### 3. ML Service (Railway)
- Créer un compte sur https://railway.app
- Déployer le dossier `ml-service/`

## Variables d'Environnement

```env
# Backend
SECRET_KEY=votre-cle-secrete
DEBUG=false
ALLOWED_HOSTS=iuc-api.onrender.com
DATABASE_URL=postgres://...
REDIS_URL=redis://...
```

## Vérification

```bash
# Tester l'API
curl https://iuc-api.onrender.com/health/

# Tester le frontend
open https://iuc-inventory.vercel.app
```