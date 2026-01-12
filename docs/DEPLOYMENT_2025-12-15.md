# Bitácora de Despliegue – 2025-12-15

Este documento registra los errores observados en Render, el análisis de causa raíz y las correcciones aplicadas en el frontend (React + TypeScript) que consume el backend FastAPI externo.

## Contexto
- Repositorio: `AndreaDu2001/Tesis-` (rama `main`).
- Servicio Render (Web con Dockerfile) y servicio Render (Static build `cd frontend && npm run build`).
- Frontend empaquetado con `react-scripts`, servido con `serve` en puerto 3000.
- Variable `REACT_APP_API_URL` controla el endpoint del backend y debe apuntar a la base sin `/api` (el código agrega `/api`).

## Errores observados en Render

1) Build vía Dockerfile
```
#13 65.87 [eslint]
src/components/Auth/Login.tsx
Syntax error: Property or signature expected (21:undefined)
```

2) Build vía comando Render (Node 22.16.0)
```
[eslint]
src/components/Auth/Login.tsx
Syntax error: Declaration or statement expected (466:undefined)
```

## Causa raíz
El archivo `frontend/src/components/Auth/Login.tsx` contenía una mezcla de dos implementaciones:
- Un componente de login simple (válido y con imports correctos).
- Un bloque adicional con pestañas (login/OTP/registro) con múltiples estados e imports no definidos en el archivo.

Esto generaba errores de sintaxis (propiedades/firma esperada) y referencias a símbolos inexistentes.

## Correcciones aplicadas y validadas localmente

### 1. Build (Compilación) – Login.tsx
- Se depuró `Login.tsx` eliminando bloque duplicado (OTP/Registro/Tabs).
- Se corrigieron props undefined agregando valor por defecto `= {}`.

### 2. Runtime – REACT_APP_API_URL
- **Problema**: `REACT_APP_API_URL` definida en stage 2 del Dockerfile (después del build). En React, las env vars solo están disponibles en tiempo de **build**, no runtime.
- **Solución**: Mover `REACT_APP_API_URL` a stage 1 (build) usando `ARG REACT_APP_API_URL` y `ENV REACT_APP_API_URL=${REACT_APP_API_URL}`.
- **Validación local**: Build Docker exitoso, contenedor ejecutándose, app respondiendo HTTP 200 con HTML correcta en `http://localhost:3003`.

## Estado actual
- ✅ Build compila sin errores (solo warnings de ESLint menores).
- ✅ Docker construye y sirve frontend correctamente.
- ✅ App React inicializa sin crashes de runtime.
- ✅ Commits pusheados a AndreaDu2001/Tesis- y Ricardo16365Travez/latacunga_limpia.

Archivos modificados:
- `frontend/src/components/Auth/Login.tsx` (commit cd00424 + e92c614)
- `Dockerfile` (commit 9144f53)

## Pasos siguientes sugeridos
1. Reconstruir localmente el frontend:
   - `cd frontend`
   - `npm install`
   - `npm run build`
2. Probar imagen Docker local:
   - `docker build -t tesis-frontend .`
   - `docker run -p 3000:3000 --env REACT_APP_API_URL="https://<tu-backend>" tesis-frontend`
3. Validar `REACT_APP_API_URL` en Render (debe ser la base sin `/api`).
4. Reintentar deploy en Render.

## Notas adicionales
- `Dockerfile` actualizado para build y serve del frontend (Node 18 alpine + `serve`).
- `render.yaml` simplificado a un solo servicio web Docker, `healthCheckPath: /`, puerto 3000, `REACT_APP_API_URL`.

