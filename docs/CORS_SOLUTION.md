# Solución CORS y Configuración Backend

## Problema CORS detectado

El frontend desplegado en `https://tesis-1-z78t.onrender.com` intenta consumir el backend en `https://tesis-c5yj.onrender.com`, pero las peticiones son bloqueadas por CORS:

```
Access to XMLHttpRequest at 'https://tesis-c5yj.onrender.com/api/conductores/mis-rutas/todas' 
from origin 'https://tesis-1-z78t.onrender.com' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solución en el Backend (FastAPI)

El backend de Andrea debe configurar CORS para permitir peticiones del frontend. En FastAPI:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tesis-1-z78t.onrender.com",  # Frontend en Render
        "http://localhost:3000",              # Frontend local desarrollo
        "http://localhost:3003",
        "http://localhost:3004",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

O para permitir cualquier origen (solo desarrollo/pruebas):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Configuración actual del frontend

- **Backend URL**: `https://tesis-c5yj.onrender.com`
- **Repo backend**: `https://github.com/Andres09xZ/epagal-backend-latacunga-route-service.git`
- **Credenciales de prueba**: `admin` / `admin123`

## Endpoints consumidos

El frontend consume los siguientes endpoints del backend:

- `POST /api/auth/login` - Autenticación JWT
- `GET /api/conductores/mis-rutas/todas` - Rutas del conductor
- `GET /api/conductores/mis-rutas/actual` - Ruta actual
- `POST /api/conductores/iniciar-ruta` - Iniciar ruta
- `POST /api/conductores/finalizar-ruta` - Finalizar ruta
- `GET /api/rutas/generar/{zona}` - Generar ruta por zona
- `GET /api/rutas/{rutaId}` - Obtener ruta
- `GET /api/rutas/{rutaId}/detalles` - Detalles de ruta
- `GET /api/incidencias/` - Listar incidencias
- `POST /api/incidencias/` - Crear incidencia
- `GET /api/incidencias/stats` - Estadísticas

## Verificación local

Para probar el backend localmente antes de configurar CORS:

```bash
curl -X POST https://tesis-c5yj.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Debería devolver:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

## Próximos pasos

1. Andrea debe agregar configuración CORS en el backend (ver código arriba)
2. Redeploy del backend en Render
3. El frontend ya está configurado para consumir `https://tesis-c5yj.onrender.com`
4. Una vez CORS esté configurado, las peticiones deberían funcionar
