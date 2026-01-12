# Dockerfile - Frontend React que consume backend de Andrea
# El backend FastAPI de Andrea es la fuente de verdad en:
# https://github.com/Andres09xZ/epagal-backend-latacunga-route-service

FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copiar manifest
COPY frontend/package.json ./
COPY frontend/package-lock.json ./

# Instalar dependencias sin exigir lockfile (lockfile actual es inválido)
RUN npm install --no-audit --no-fund --legacy-peer-deps

# Copiar resto del código
COPY frontend ./

# Variables de entorno para build (CRÍTICO: deben estar en stage 1)
ARG REACT_APP_API_BASE=https://epagal-backend-routing-latest.onrender.com
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}
ENV NODE_ENV=production
ENV CI=false

# Build optimizado
RUN npm run build

# Stage 2: Servir frontend con Express (para SPA routing)
FROM node:18-alpine

WORKDIR /app

# Instalar express como dependencia de producción
RUN npm install express@^4.18.2

# Copiar servidor Express personalizado
COPY frontend/server.js ./server.js

# Copiar build del frontend
COPY --from=frontend-build /app/frontend/build ./build

EXPOSE 3000

# Variables de entorno para runtime
ENV NODE_ENV=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Servir frontend con Express (maneja SPA routing correctamente)
CMD ["node", "server.js"]
