#!/bin/bash
# Script de diagnóstico para verificar backend FastAPI

echo "=== DIAGNÓSTICO DEL BACKEND ==="
echo ""

# 1. Verificar que el backend está en línea
echo "1. Verificando disponibilidad del backend..."
BACKEND_URL="https://epagal-backend-routing-latest.onrender.com"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)

if [ "$STATUS" = "200" ]; then
  echo "✅ Backend disponible (status: $STATUS)"
else
  echo "❌ Backend no responde o está down (status: $STATUS)"
fi

echo ""

# 2. Verificar endpoint de login
echo "2. Verificando endpoint de login..."
LOGIN_URL="$BACKEND_URL/api/auth/login"
echo "   URL: $LOGIN_URL"

# Hacer request OPTIONS para ver headers CORS
echo "   Probando con OPTIONS (CORS)..."
curl -s -X OPTIONS "$LOGIN_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -H "Origin: https://tesis-1-z78t.onrender.com" \
  -v 2>&1 | grep -E "(HTTP|Access-Control)"

echo ""

# 3. Intentar login con credenciales de prueba
echo "3. Intentando login con credenciales de prueba..."
curl -s -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "admin@latacunga.gob.ec",
    "username": "admin@latacunga.gob.ec",
    "password": "admin123"
  }' | jq . 2>/dev/null || echo "   No se pudo parsear respuesta"

echo ""
echo "=== FIN DEL DIAGNÓSTICO ==="
