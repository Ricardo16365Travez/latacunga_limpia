# Dockerfile - Frontend React que consume backend de Andrea
# El backend FastAPI de Andrea es la fuente de verdad en:
# https://github.com/Andres09xZ/epagal-backend-latacunga-route-service

FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copiar package.json
COPY frontend/package.json ./

# Instalar dependencias
RUN npm install --prefer-offline --no-audit 2>&1 | tail -5

# Copiar resto del código
COPY frontend ./

# Variables de entorno para build (CRÍTICO: deben estar en stage 1)
ARG REACT_APP_API_URL=https://tesis-c5yj.onrender.com
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV NODE_ENV=production
ENV CI=false

# Build optimizado
RUN npm run build

# Stage 2: Servir frontend
FROM node:18-alpine

WORKDIR /app

# Instalar 'serve' para servir estáticos
RUN npm install -g serve

# Copiar build del frontend
COPY --from=frontend-build /app/frontend/build ./build

EXPOSE 3000

# Variables de entorno para runtime (informativas)
ENV NODE_ENV=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Servir frontend
CMD ["serve", "-s", "build", "-l", "3000"]
