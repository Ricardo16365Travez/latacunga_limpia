# 🤖 DEVOPS AUTOMATIZADO - RENDER + GITHUB ACTIONS

## ✅ QUÉ SE IMPLEMENTÓ

### 1. **Dockerfile Corregido** ✅
```dockerfile
- Multi-stage build
- Incluye GDAL/PostGIS para GeoDjango
- Expone puerto 10000 (compatible con Render)
- Health check integrado
- Optimizado para producción
```

### 2. **Configuración Render (render.yaml)** ✅
```yaml
Backend Web Service:
  - Plan: Free
  - Runtime: Docker
  - Health Check: /health/
  - Workers: 2
  - Timeout: 120s

Frontend Static Site:
  - Plan: Free
  - Build: npm build
  - Routes: Redirección a index.html

Base de Datos (Opcional):
  - PostgreSQL 15 con PostGIS
  - Plan Starter ($7/mes)
```

### 3. **CI/CD con GitHub Actions** ✅

#### **Workflow 1: Deploy** (.github/workflows/deploy.yml)
**Triggers:** Push a `prototipo` o `main`
**Steps:**
1. Test Backend (pytest + db)
2. Test Frontend (build + lint)
3. Build Docker image
4. Notify Render (webhook)
5. Slack notification (opcional)

**Duración:** ~5-10 minutos

#### **Workflow 2: Code Quality** (.github/workflows/code-quality.yml)
**Triggers:** Push o Pull Request
**Checks:**
- Seguridad (Trivy)
- Python (flake8, black, isort)
- TypeScript (ESLint, tsc)
- Dependencias (safety, npm audit)

**Beneficio:** Detecta problemas antes de merge

#### **Workflow 3: Health Check** (.github/workflows/health-check.yml)
**Triggers:** Cada 30 minutos (schedule)
**Checks:**
- Backend health endpoint
- Frontend status
- API endpoints (incidents, tasks)
- Database connection
- Uptime tracking

**Beneficio:** Monitoreo automático 24/7

### 4. **Optimizaciones** ✅
- `.dockerignore` - Reduce tamaño de build
- `requirements.txt` con versiones pinned
- `render-build.sh` - Setup automatizado
- `render-complete.yaml` - Config avanzada

---

## 🚀 CÓMO FUNCIONA EL PIPELINE

```
┌─────────────────────────────────────────┐
│  PUSH A GITHUB (prototipo branch)        │
└─────────────────────────────────────────┘
                    ↓
    ┌───────────────┬───────────────┐
    ↓               ↓               ↓
[Test Backend] [Test Frontend] [Code Quality]
    ↓               ↓               ↓
    └───────────────┬───────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ BUILD DOCKER IMAGE                │
    │ (Render lo detecta automáticamente)│
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ RENDER DEPLOY                      │
    │ • Build imagen                     │
    │ • Migrations                       │
    │ • Static files                     │
    │ • Start gunicorn                   │
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ NOTIFICATIONS                      │
    │ • GitHub (✓ o ✗)                  │
    │ • Slack (si está configurado)      │
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ HEALTH CHECK (cada 30 min)         │
    │ • Backend /health/                 │
    │ • Frontend /                       │
    │ • API endpoints                    │
    │ • Database connection              │
    └───────────────────────────────────┘
```

---

## 📋 WORKFLOW DEPLOY DETALLADO

### **Phase 1: Testing Backend**
```bash
1. Instalar dependencias (+ cache)
2. Spinup PostgreSQL + PostGIS
3. Run flake8 (linting)
4. Run migrations
5. Run pytest
```

### **Phase 2: Testing Frontend**
```bash
1. Instalar node_modules (+ cache)
2. Lint con ESLint
3. npm run build
4. Optimización automática
```

### **Phase 3: Docker Build**
```bash
1. Buildx setup
2. Multi-stage Docker build
3. Cache optimization (GHA)
4. Push si necesario
```

### **Phase 4: Render Notification**
```bash
1. Si todos los tests pasaron:
   curl https://api.render.com/deploy?hook=...
2. Render inicia build automáticamente
3. Deploy en 3-5 minutos
```

---

## 🔐 SECRETS NECESARIOS EN GITHUB

Para funcionalidad completa, configura en:
**Repo Settings → Secrets and variables → Actions**

```
RENDER_DEPLOY_HOOK = https://api.render.com/deploy/srv-xxx
DATABASE_URL = postgresql://user:pass@host/db  (para tests)
SLACK_WEBHOOK_URL = https://hooks.slack.com/... (opcional)
```

**Cómo obtenerlos:**
1. **RENDER_DEPLOY_HOOK:**
   - Render Dashboard → Web Service
   - Settings → Deploy hooks
   - Copiar URL

2. **DATABASE_URL (para tests):**
   - Render DB o Supabase
   - Connection string
   - o dejar vacío (usa PostgreSQL de Actions)

3. **SLACK_WEBHOOK_URL:**
   - Slack App → Incoming Webhooks
   - Create new webhook
   - Copiar URL

---

## ⚙️ CONFIGURACIÓN EN RENDER

### **Paso 1: Conectar GitHub**
1. Render Dashboard → Web Service → Create
2. Conectar repositorio: `Ricardo16365Travez/latacunga_limpia`
3. Rama: `prototipo`
4. **IMPORTANTE:** Render detecta automáticamente `Dockerfile` en raíz

### **Paso 2: Variables de Entorno**
En Render Dashboard, agregar:
```
DEBUG = False
ENVIRONMENT = production
SECRET_KEY = (generar con: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS = residuos-backend.onrender.com
DATABASE_URL = postgresql://...
REDIS_URL = redis://... (si usas Redis)
```

### **Paso 3: Health Check (Render)**
```
Health Check Path: /health/
Startup Timeout: 300s
Check Interval: 60s
```

### **Paso 4: Deploy Hook (opcional)**
```
Generar en: Settings → Deploy hooks
Agregar a GitHub Secrets como: RENDER_DEPLOY_HOOK
```

---

## 🧪 VERIFICACIÓN POST-DEPLOY

### **Manual Testing:**
```bash
# 1. Frontend accesible
curl https://residuos-frontend.onrender.com

# 2. Backend health
curl https://residuos-backend.onrender.com/health/

# 3. API funcional
curl https://residuos-backend.onrender.com/api/incidents/

# 4. Login
curl -X POST https://residuos-backend.onrender.com/api/login/ \
  -d "email=admin@latacunga.gob.ec&password=admin123"
```

### **GitHub Actions Checks:**
1. Click en último commit
2. "Actions" tab
3. Ver status de workflows
4. Click para ver detalles

### **Render Logs:**
1. Render Dashboard
2. Web Service
3. "Logs" tab
4. Ver build y runtime logs

---

## 📊 MONITORED METRICS

El Health Check workflow monitorea:

| Métrica | Check | Frecuencia |
|---------|-------|-----------|
| Backend Status | HTTP 200 a /health/ | 30 min |
| Frontend Status | HTTP 200 a / | 30 min |
| API /incidents | Response time | 30 min |
| API /tasks | Response time | 30 min |
| Database | Connection + version | 30 min |
| Uptime | Total de horas | Diario |

---

## 🔄 FLUJO COMPLETO EJEMPLO

**Escenario:** Cambio en `backend/apps/tasks/views.py`

```
1. [LOCAL] Editar archivo
2. [LOCAL] git add, commit, push
3. [GITHUB] Trigger workflow "Deploy"
4. [GITHUB] Test Backend - pytest runs
5. [GITHUB] Test Frontend - build runs
6. [GITHUB] Docker build
7. [GITHUB] Notificación a Render
8. [RENDER] Webhook recibido
9. [RENDER] Build Docker image
10. [RENDER] Run migrations
11. [RENDER] Collectstatic
12. [RENDER] Start gunicorn
13. [GITHUB] Notificación en Slack (if configured)
14. [GITHUB] Health check runs cada 30 min
15. ✅ Cambios en producción en ~5-7 min
```

---

## 🐛 TROUBLESHOOTING

### Error: "Dockerfile not found"
```bash
✅ SOLUCIONADO - Dockerfile ahora en raíz
git pull origin prototipo
```

### Tests fallan en GitHub Actions
```
1. Ver logs: Repo → Actions → workflow
2. Revisar errores específicos
3. Fijar en local y push nuevamente
4. Workflow reinicia automáticamente
```

### Render deploy no inicia
```
1. Verificar render.yaml existe
2. Verificar Dockerfile es válido
3. Verificar secretos configurados
4. Ver logs en Render Dashboard
```

### Health check falla
```
1. Render puede estar redeployando
2. Esperar 2-3 minutos
3. Verificar con: curl https://residuos-backend.onrender.com/health/
4. Si persiste, revisar logs en Render
```

---

## 📈 PRÓXIMOS PASOS

### **Fase 1 (AHORA):**
- ✅ Dockerfile funcionando
- ✅ GitHub Actions configurado
- ✅ Health check activo

### **Fase 2 (Opcional):**
- [ ] Agregar BD PostgreSQL en Render
- [ ] Configurar Redis
- [ ] Notificaciones en Slack
- [ ] Analytics y monitoring

### **Fase 3 (Avanzado):**
- [ ] Blue-green deployment
- [ ] Canary deployment
- [ ] Auto-scaling
- [ ] Load balancing

---

## 💾 ARCHIVOS NUEVOS

```
.github/
├── workflows/
│   ├── deploy.yml              # Deploy automático
│   ├── code-quality.yml        # Análisis de código
│   └── health-check.yml        # Monitoreo 24/7

Dockerfile                       # Imagen Docker completa
.dockerignore                    # Optimizar build
render.yaml                      # Config para Render
render-build.sh                  # Script setup
render-complete.yaml             # Config avanzada
DOCKER_RENDER_FIXED.md          # Guía corección
```

---

## 🎉 RESULTADO FINAL

**Automatización Completa:**
- ✅ CI/CD pipeline end-to-end
- ✅ Tests automáticos
- ✅ Code quality checks
- ✅ Docker build optimizado
- ✅ Deploy a Render automático
- ✅ Health monitoring 24/7
- ✅ Notifications (GitHub + Slack)
- ✅ Sin intervención manual

**Deploy Time:** 5-7 minutos desde push a producción

**Uptime Tracking:** Automático con health checks

**Next Deployment:** Ocurre automáticamente cada push a `prototipo`

---

**¡Tu DevOps está 100% automatizado! 🚀**
