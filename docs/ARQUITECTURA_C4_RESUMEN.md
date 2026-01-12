# Resumen de Arquitectura (C4)

Este documento resume la arquitectura siguiendo el modelo C4 (Contexto, Contenedores, Componentes). Se ampliará en la memoria de tesis.

## Contexto (Nivel 1)
- Actor principal: Operador municipal (gestiona rutas, incidencias).
- Sistema frontend React (esta app) consume un backend FastAPI externo.
- Integraciones: API de rutas/operadores/incidencias en el backend.

## Contenedores (Nivel 2)
- Frontend Web (React + TS)
  - Desplegado como contenedor (Docker) y/o estático (Render).
  - Sirve UI en puerto 3000, consume API vía `REACT_APP_API_URL`.
- Backend (FastAPI)
  - Servicio externo (fuera de este repo). Expone `/api/...` (auth, rutas, incidencias).
- Base de datos
  - Gestionada por el backend externo.

## Componentes (Nivel 3) – Frontend
- `config/api.ts`: Construye `API_BASE_URL` (agrega `/api` si falta) y rutas.
- `services/apiService.ts`: Cliente Axios con interceptores JWT.
- `components/Auth/Login.tsx`: Autenticación básica (usuario/contraseña).
- `services/*`: Servicios para rutas, conductores, incidencias.

## Decisiones clave
- Separación Frontend/Backend: El frontend es agnóstico y configurable por env var.
- Distribución: Dockerfile multi-stage para build y `serve` para producción.
- Observabilidad: `healthCheckPath: /` en Render, expuesto 3000.

## Próximos pasos de documentación
- Diagrama C4 formal (Context, Container, Component) en formato imagen.
- Riesgos/NFRs: rendimiento, seguridad (JWT), CORS, disponibilidad.
- Estrategia de despliegue y rollback en Render.
