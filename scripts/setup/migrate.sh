#!/bin/bash
echo "========================================="
echo "  IUC Inventory - Migrations initiales"
echo "========================================="
echo ""

cd /app

echo "1. Création des migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations roles
python manage.py makemigrations departments
python manage.py makemigrations campuses
python manage.py makemigrations warehouses
python manage.py makemigrations categories
python manage.py makemigrations products
python manage.py makemigrations suppliers
python manage.py makemigrations purchase_orders
python manage.py makemigrations stock_movements
python manage.py makemigrations inventories
python manage.py makemigrations notifications

echo ""
echo "2. Application des migrations..."
python manage.py migrate

echo ""
echo "3. Création du superuser..."
python manage.py createsuperuser --noinput \
    --email admin@iuc.cm \
    --matricule ADMIN001 \
    --first_name Admin \
    --last_name IUC \
    --role ADMIN || true

echo ""
echo "✓ Migrations terminées!"
