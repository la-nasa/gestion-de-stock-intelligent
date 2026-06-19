# Guide de Déploiement - IUC Inventory System

## Déploiement Production

### Architecture de Production

```
                   ┌─────────────┐
                   │   Nginx     │ (Reverse Proxy + SSL)
                   └──────┬──────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐  ┌──────▼──────┐  ┌────▼─────┐
    │ Frontend  │  │  Backend    │  │    ML    │
    │ Next.js   │  │  Django x3  │  │ Service  │
    └───────────┘  └──────┬──────┘  └──────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐  ┌──────▼──────┐  ┌────▼─────┐
    │PostgreSQL │  │   Redis     │  │ RabbitMQ │
    │  Master   │  │   Cluster   │  │          │
    └─────┬─────┘  └─────────────┘  └──────────┘
          │
    ┌─────▼─────┐
    │PostgreSQL │
    │  Replica  │
    └───────────┘
```

### 1. Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y \
    docker.io \
    docker-compose-v2 \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw

# Configuration du firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Démarrer Docker
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Configuration SSL

```bash
# Obtenir un certificat SSL
sudo certbot --nginx -d inventory.iuc.cm -d api.iuc.cm

# Renouvellement automatique
sudo certbot renew --dry-run
```

### 3. Configuration Nginx

```nginx
# /etc/nginx/sites-available/iuc-inventory
server {
    listen 80;
    server_name inventory.iuc.cm;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name inventory.iuc.cm;

    ssl_certificate /etc/letsencrypt/live/inventory.iuc.cm/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/inventory.iuc.cm/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    client_max_body_size 50M;
}
```

### 4. Déploiement avec Docker Compose

```bash
# Cloner le projet
cd /opt
git clone https://github.com/iuc/inventory-system.git
cd inventory-system/docker

# Configurer l'environnement
cp .env.example .env
nano .env  # Modifier les valeurs de production

# Variables critiques à modifier :
# SECRET_KEY=<générer-une-clé-longue>
# DB_PASSWORD=<mot-de-passe-sécurisé>
# REDIS_PASSWORD=<mot-de-passe-sécurisé>
# DEBUG=false
# ENVIRONMENT=production
# ALLOWED_HOSTS=inventory.iuc.cm,api.iuc.cm

# Démarrer les services
docker-compose -f docker-compose.yml up -d

# Vérifier l'état
docker-compose ps
```

### 5. Backup Automatique

```bash
# Créer le script de backup
cat > /opt/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/iuc-inventory"
DATE=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
docker exec iuc_postgres pg_dump -U iuc_user iuc_inventory | \
    gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup fichiers uploadés
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /opt/inventory-system/backend/media/

# Nettoyage anciens backups
find "$BACKUP_DIR" -mtime +$RETENTION_DAYS -delete
EOF

chmod +x /opt/scripts/backup.sh

# Ajouter au crontab (quotidien à 2h)
echo "0 2 * * * /opt/scripts/backup.sh" | crontab -
```

### 6. Monitoring

```bash
# Accéder à Grafana
# URL: https://inventory.iuc.cm:3001
# User: admin (configurer dans .env)

# Dashboards préconfigurés :
# - Vue d'ensemble système
# - Performance API
# - État base de données
# - Métriques métier

# Alertes configurées :
# - CPU > 80%
# - Mémoire > 85%
# - Disque > 90%
# - API temps réponse > 2s
# - Taux erreurs > 5%
```

### 7. Mise à Jour

```bash
cd /opt/inventory-system
git pull origin main

cd docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Vérifier les migrations
docker exec iuc_backend python manage.py migrate --noinput
docker exec iuc_backend python manage.py collectstatic --noinput
```

### 8. Rollback

```bash
# Revenir à la version précédente
git log --oneline -5
git checkout <commit-hash>

docker-compose down
docker-compose build --no-cache
docker-compose up -d
```



## Checklist Déploiement

- [ ] SSL configuré et valide
- [ ] Firewall actif (ports 80, 443 uniquement)
- [ ] Variables d'environnement sécurisées
- [ ] DEBUG = false
- [ ] Backup automatique configuré
- [ ] Monitoring actif (Grafana)
- [ ] Logs centralisés (Sentry)
- [ ] Rate limiting configuré
- [ ] Health checks OK
- [ ] Tests de charge effectués
- [ ] Documentation accessible