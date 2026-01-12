# Configuración de GitHub Actions para Deploy Automático

## Paso 1: Obtener Render API Key
1. Ve a https://dashboard.render.com/account/api-tokens
2. Crea un nuevo token o copia uno existente
3. Copia el token (lo necesitarás en el Paso 4)

## Paso 2: Obtener Render Service ID del Frontend
1. Ve a https://dashboard.render.com
2. Haz clic en tu servicio de frontend (Tesis-)
3. En la URL verás algo como: `https://dashboard.render.com/web/srv-abc123def456...`
4. El ID es lo que viene después de `/srv-` (ejemplo: `abc123def456ghi789`)
5. Copia ese ID (lo necesitarás en el Paso 4)

## Paso 3: Ir a GitHub
1. Abre https://github.com/AndreaDu2001/Tesis-
2. Ve a Settings → Secrets and variables → Actions
3. Haz clic en "New repository secret"

## Paso 4: Agregar los Secrets
Crea dos secrets:

### Secret 1: RENDER_API_KEY
- **Name:** `RENDER_API_KEY`
- **Value:** Tu API key de Render (del Paso 1)
- Haz clic en "Add secret"

### Secret 2: RENDER_SERVICE_ID  
- **Name:** `RENDER_SERVICE_ID`
- **Value:** El ID del servicio frontend (del Paso 2)
- Haz clic en "Add secret"

## Cómo Funciona el Workflow

Ahora cada vez que hagas **push a la rama `main`** en la carpeta `frontend/`:
1. GitHub Actions ejecutará el workflow automáticamente
2. El workflow llamará a la API de Render para triggear un deploy
3. Render detectará el cambio y deployará la nueva versión

## Verificar que Funciona

1. Haz un pequeño cambio en `frontend/src/...`
2. Commit y push a main:
   ```bash
   git add frontend/
   git commit -m "test: verify github actions workflow"
   git push origin main
   ```
3. Ve a https://github.com/AndreaDu2001/Tesis-/actions
4. Deberías ver que el workflow está ejecutándose (círculo azul)
5. Espera a que termine (check verde = éxito)
6. Verifica en Render que el deploy se está ejecutando

## Notas Importantes

- ❌ El backend NO se deployará automáticamente (solo el frontend)
- ✅ Cada push a `main` en la carpeta `frontend/` dispara el deploy
- ✅ Los cambios en `backend/` NO disparan este workflow
- 🔒 Los secrets están encriptados y no se ven en los logs
