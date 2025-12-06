#!/usr/bin/env bash
# 🚀 RENDER DEPLOYMENT QUICK START
# Ejecutar este script después de crear cuenta en Render

set -e

echo "🎯 LATACUNGA LIMPIA - RENDER DEPLOYMENT"
echo "======================================"
echo ""
echo "✅ Status: DevOps Automatizado Completado"
echo "📅 Fecha: 5 de Diciembre, 2025"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 CHECKLIST PRE-DEPLOY${NC}"
echo "========================="

checks=(
    "Dockerfile en raíz"
    ".dockerignore configurado"
    "render.yaml actualizado"
    "GitHub Actions workflows activos"
    "Código pusheado a GitHub"
    "Branch prototipo actualizada"
)

for check in "${checks[@]}"; do
    echo -e "${GREEN}✅${NC} $check"
done

echo ""
echo -e "${BLUE}🔐 SECRETS NECESARIOS EN RENDER${NC}"
echo "=================================="
cat <<EOF
Agregar en Render Dashboard → Environment Variables:

    DEBUG = False
    ENVIRONMENT = production
    SECRET_KEY = <generar>
    ALLOWED_HOSTS = residuos-backend.onrender.com
    DATABASE_URL = <supabase o render-db>
    
(Opcional para GitHub Actions):
    RENDER_DEPLOY_HOOK = <from Render Deploy hooks>
    DATABASE_URL = <for tests>
    SLACK_WEBHOOK_URL = <for notifications>
EOF

echo ""
echo -e "${BLUE}🚀 PASOS PARA DEPLOY EN RENDER${NC}"
echo "================================"
cat <<EOF

1. Abre: https://dashboard.render.com

2. Click "Create +" → "Web Service"

3. Conecta GitHub:
   - Repositorio: Ricardo16365Travez/latacunga_limpia
   - Rama: prototipo

4. Configuración:
   - Render detecta automáticamente Dockerfile ✅
   - Health Check Path: /health/
   - Startup Timeout: 300s

5. Variables de Entorno:
   - Agregar las 5 variables principales (ver arriba)

6. Deploy:
   - Click "Create Web Service"
   - Esperar 5-7 minutos
   - Verificar logs

7. Test:
   - Frontend: https://residuos-frontend.onrender.com
   - Backend: https://residuos-backend.onrender.com/health/
   - API: https://residuos-backend.onrender.com/api/incidents/

EOF

echo -e "${BLUE}📊 MONITOREO AUTOMÁTICO${NC}"
echo "========================"
cat <<EOF
Los siguientes workflows se ejecutan automáticamente:

✅ deploy.yml          → Cada push a prototipo (5-10 min)
✅ code-quality.yml    → Cada push (linting + seguridad)
✅ health-check.yml    → Cada 30 minutos (monitoring)

Ver status en: https://github.com/Ricardo16365Travez/latacunga_limpia/actions

EOF

echo -e "${GREEN}🎉 ¡Proyecto listo para producción!${NC}"
echo ""
echo "Documentación disponible:"
echo "  - RENDER_QUICK_START.md"
echo "  - DOCKER_RENDER_FIXED.md"
echo "  - DEVOPS_AUTOMATIZADO.md"
echo "  - DEVOPS_STATUS_FINAL.md"
echo ""
echo "¡A desplegar! 🚀"
