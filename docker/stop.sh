#!/bin/bash
set -e

echo "========================================"
echo "  Stopping IUC Inventory System..."
echo "========================================"

docker-compose down

echo ""
echo "✓ All services stopped"
echo ""
echo "To remove all data volumes:"
echo "  docker-compose down -v"
