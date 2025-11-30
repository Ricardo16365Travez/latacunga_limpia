#!/bin/bash
# Script para probar el sistema con Docker

echo "========================================="
echo "PRUEBA DEL SISTEMA - Docker"
echo "========================================="

echo ""
echo "1. Verificando servicios Docker..."
docker-compose ps

echo ""
echo "2. Verificando configuración Django..."
docker-compose exec -T backend python manage.py check --deploy

echo ""
echo "3. Verificando migraciones pendientes..."
docker-compose exec -T backend python manage.py showmigrations

echo ""
echo "4. Creando migraciones si es necesario..."
docker-compose exec -T backend python manage.py makemigrations

echo ""
echo "5. Listando endpoints disponibles..."
docker-compose exec -T backend python manage.py show_urls | grep -E "api/(tasks|routes|notifications|reports)"

echo ""
echo "========================================="
echo "PRUEBA COMPLETADA"
echo "========================================="
