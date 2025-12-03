# 🔧 GUÍA DE SOLUCIÓN: Error al Cargar Datos

## Problema Diagnosticado

El frontend muestra "Error al cargar datos" en todas las funcionalidades. Esto es porque:
1. **Docker no está respondiendo correctamente** en tu sistema
2. Los contenedores no pueden iniciarse
3. El backend no está accesible

## ✅ Solución Paso a Paso

### Paso 1: Reiniciar Docker Desktop Completamente

**En Windows:**

1. Abre **Task Manager** (Ctrl+Shift+Esc)
2. Busca "Docker Desktop"
3. Haz clic derecho → "Finalizar tarea"
4. Espera 5 segundos
5. Abre Docker Desktop nuevamente:
   - Opción A: Desde el Menú Inicio → "Docker Desktop"
   - Opción B: Click en el icono de Docker si está en la bandeja del sistema

6. **Espera 2-3 minutos** a que Docker inicie completamente
   - Verás un tooltip "Docker is running" cuando esté listo

### Paso 2: Iniciar los Servicios

Abre PowerShell en la carpeta del proyecto:

```powershell
cd C:\Users\trave\OneDrive\Documentos\tesisAndrea

# Detener servicios anteriores
docker-compose down

# Iniciar servicios (espera 30-60 segundos)
docker-compose up -d

# Verificar que están corriendo
docker ps
```

**Deberías ver:**
```
NAMES                  STATUS           PORTS
residuos_db           Up 2 minutes     5433->5432/tcp
residuos_backend      Up 2 minutes     8000->8000/tcp
residuos_frontend     Up 2 minutes     3001->3000/tcp
```

### Paso 3: Cargar Datos de Prueba

```powershell
docker-compose exec backend python load_sample_data.py
```

**Deberías ver:**
```
🚀 Iniciando carga de datos de prueba...
✅ Usuario admin creado
✅ 2 zonas de limpieza creadas
✅ 5 tareas de prueba creadas
✅ 5 notificaciones de prueba creadas
✅ 3 reportes de prueba creados

✨ Carga de datos completada exitosamente!
```

### Paso 4: Verificar Endpoints

En PowerShell, copia y ejecuta esto:

```powershell
$baseUrl = 'http://localhost:8000/api'

# Probar cada endpoint
Write-Host "Probando /api/incidents/..."
(Invoke-WebRequest -Uri "$baseUrl/incidents/?limit=1").StatusCode

Write-Host "Probando /api/tasks/..."
(Invoke-WebRequest -Uri "$baseUrl/tasks/?limit=1").StatusCode

Write-Host "Probando /api/routes/..."
(Invoke-WebRequest -Uri "$baseUrl/routes/?limit=1").StatusCode

Write-Host "Probando /api/notifications/..."
(Invoke-WebRequest -Uri "$baseUrl/notifications/?limit=1").StatusCode

Write-Host "Probando /api/reports/statistics/..."
(Invoke-WebRequest -Uri "$baseUrl/reports/statistics/").StatusCode
```

**Si ves "200" en todos → ¡Funciona!** ✅

### Paso 5: Abrir la Aplicación

1. Abre tu navegador
2. Ve a: **http://localhost:3001**
3. Deberías ver el dashboard con datos

---

## 🔍 Si Sigue Sin Funcionar

### 1. Revisar Logs del Backend

```powershell
docker-compose logs backend
```

Copia los últimos 50 líneas de error y comparte conmigo.

### 2. Revisar Consola del Navegador

1. Abre http://localhost:3001
2. Presiona **F12** para abrir herramientas de desarrollador
3. Ve a la pestaña **"Console"**
4. Copia todos los mensajes de error en rojo

### 3. Revisar Network

1. En las herramientas de desarrollador, ve a la pestaña **"Network"**
2. Recarga la página (Ctrl+R)
3. Busca llamadas que digan "incidents" o "tasks"
4. Haz click en una y ve la respuesta
5. Copia el error exacto

### 4. Ver Logs Detallados

```powershell
# Ver logs del frontend
docker-compose logs frontend

# Ver logs del backend en tiempo real
docker-compose logs -f backend
```

---

## 🛠️ Soluciones Específicas

### Problema: "Docker no está disponible"
**Solución:**
1. Abre Docker Desktop desde el menú Inicio
2. Espera a que el indicador diga "Docker is running"
3. Reinicia PowerShell

### Problema: "unable to get image"
**Solución:**
1. Reinicia Docker Desktop (ver Paso 1)
2. Ejecuta: `docker pull nginx:alpine`
3. Espera a que descargue
4. Luego intenta nuevamente `docker-compose up -d`

### Problema: "port 3001 already in use"
**Solución:**
```powershell
# Ver qué está usando el puerto 3001
netstat -ano | findstr :3001

# Matar el proceso (reemplaza PID)
taskkill /PID <PID> /F
```

### Problema: "ConnectionError: Connection refused"
**Solución:**
- El backend aún no está listo
- Espera 30 segundos más
- Luego recarga el navegador

---

## 📊 Valores Esperados Después de Solucionar

Una vez que todo funcione, deberías ver:

**Página de Incidencias:**
- 16+ incidencias listadas
- Campos: tipo, descripción, estado, dirección

**Página de Tareas:**
- 5+ tareas listadas
- Campos: título, descripción, estado, prioridad

**Página de Rutas:**
- 4+ rutas listadas
- Mapa con líneas de ruta visible

**Página de Notificaciones:**
- 5+ notificaciones listadas
- Opción para marcar como leída

**Página de Reportes:**
- Gráficas con estadísticas compiladas
- Números de incidencias por estado/tipo

---

## 🚨 Si Nada de Esto Funciona

Por favor ejecuta y comparte el output de:

```powershell
# 1. Información del sistema
docker --version
docker-compose --version

# 2. Estado de contenedores
docker ps -a

# 3. Logs del backend
docker-compose logs backend | Select-Object -Last 50

# 4. Logs del frontend
docker-compose logs frontend | Select-Object -Last 50

# 5. Test simple
curl -v http://localhost:8000/api/incidents/ 2>&1 | Select-Object -First 30
```

---

## 📝 Cambios Realizados en Este Commit

✅ Actualizado permission_classes en todos los viewsets a `IsAuthenticatedOrReadOnly`  
✅ Esto permite hacer GET (lectura) sin autenticación  
✅ El frontend ahora puede cargar datos sin necesidad de token  

Los cambios están en:
- `backend/apps/tasks/views.py`
- `backend/apps/notifications/views.py`
- `backend/apps/routes/views.py`
- `backend/apps/reports/views.py`

---

**Siempre puedes ver el estado actual con:**
```powershell
docker ps        # Ver contenedores corriendo
docker logs NAME # Ver logs de un contenedor
docker-compose logs -f backend  # Ver logs en tiempo real
```
