#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/backups"
DB_NAME="iuc_inventory"
DB_USER="iuc_user"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "  IUC Inventory System - Backup"
echo "========================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo -e "${YELLOW}Backing up database...${NC}"
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h localhost \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F c \
    -b \
    -v \
    -f "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Backup media files
echo -e "${YELLOW}Backing up media files...${NC}"
tar -czf "$BACKUP_DIR/media_${TIMESTAMP}.tar.gz" -C /app media/

# Backup static files
echo -e "${YELLOW}Backing up static files...${NC}"
tar -czf "$BACKUP_DIR/static_${TIMESTAMP}.tar.gz" -C /app staticfiles/

# Encrypt backup
echo -e "${YELLOW}Encrypting backup...${NC}"
gpg --encrypt --recipient backup@iuc.cm "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Clean old backups
echo -e "${YELLOW}Cleaning old backups...${NC}"
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo ""
echo -e "${GREEN}✓ Backup completed successfully!${NC}"
echo "  Database: ${DB_NAME}_${TIMESTAMP}.dump"
echo "  Media: media_${TIMESTAMP}.tar.gz"
echo "  Static: static_${TIMESTAMP}.tar.gz"
