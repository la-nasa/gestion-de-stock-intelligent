.PHONY: help start stop restart logs status clean

# Default target
help:
    @echo "IUC Inventory System - Commandes Docker"
    @echo "========================================"
    @echo ""
    @echo "  make start      Démarrer tous les services"
    @echo "  make stop       Arrêter tous les services"
    @echo "  make restart    Redémarrer tous les services"
    @echo "  make logs       Voir les logs"
    @echo "  make status     Voir le statut des services"
    @echo "  make clean      Nettoyer tous les conteneurs et volumes"
    @echo ""

start:
    @bash start.sh

stop:
    @bash stop.sh

restart:
    @bash stop.sh
    @bash start.sh

logs:
    docker-compose logs -f

status:
    docker-compose ps

clean:
    docker-compose down -v
    rm -rf data/
    @echo "✓ Nettoyage terminé"
