#!/bin/bash
set -e

echo "========================================"
echo "  IUC Inventory System - Startup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file with your settings before continuing${NC}"
    exit 1
fi

# Function to wait for service
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${CYAN}Waiting for $service on port $port...${NC}"
    while ! nc -z localhost $port && [ $attempt -le $max_attempts ]; do
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -le $max_attempts ]; then
        echo -e "${GREEN}✓ $service is ready!${NC}"
    else
        echo -e "${RED}✗ $service failed to start${NC}"
        exit 1
    fi
}

# Start services
echo -e "${CYAN}Starting all services...${NC}"
docker-compose up -d

echo ""
echo -e "${CYAN}Waiting for services to be ready...${NC}"
wait_for_service "Backend" 8000
wait_for_service "Frontend" 3000
wait_for_service "ML Service" 8001

echo ""
echo -e "${GREEN}========================================"
echo "  ALL SERVICES ARE RUNNING !"
echo "========================================"
echo ""
echo "  Frontend:    http://localhost:3000"
echo "  Backend:     http://localhost:8000"
echo "  API Docs:    http://localhost:8000/swagger/"
echo "  ML Service:  http://localhost:8001/docs"
echo "  Grafana:     http://localhost:3001"
echo "  Flower:      http://localhost:5555"
echo "  MinIO:       http://localhost:9001"
echo "  RabbitMQ:    http://localhost:15672"
echo ""
echo -e "${NC}"
