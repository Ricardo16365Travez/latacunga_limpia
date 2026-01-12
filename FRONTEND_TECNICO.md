# Frontend Técnico - EPAGAL Latacunga

## Estructura del Proyecto Frontend

```
frontend/src/
├── App.tsx                    # Root component + routing
├── index.tsx                  # Entry point
├── index.css                  # Global styles
│
├── components/
│   ├── Auth/
│   │   └── Login.tsx         # Login form
│   │
│   ├── Dashboard/
│   │   └── Dashboard.tsx     # Main dashboard
│   │
│   ├── Layout/
│   │   ├── Sidebar.tsx       # Navigation menu
│   │   └── Dashboard.tsx     # Layout wrapper
│   │
│   ├── Incidents/
│   │   └── IncidentsPage.tsx # Incident list + map
│   │
│   ├── Routes/
│   │   ├── GeneracionRutas.tsx   # Route generator
│   │   ├── MisRutas.tsx          # My routes list
│   │   ├── RutaDetalle.tsx       # Route detail + map
│   │   ├── LiveTracking.tsx      # Real-time tracking
│   │   └── RoutesPage.tsx        # Routes hub
│   │
│   ├── Notifications/
│   │   └── NotificationsPage.tsx
│   │
│   ├── Reports/
│   │   └── ReportsPage.tsx   # Statistics & charts
│   │
│   └── common/
│       ├── Header.tsx        # Top bar
│       ├── ErrorBoundary.tsx # Error handling
│       └── Loading.tsx       # Loading spinner
│
├── services/
│   ├── apiService.ts        # Axios config + interceptors
│   ├── incidenciasService.ts
│   ├── rutasService.ts
│   ├── conductoresService.ts
│   ├── reportesService.ts
│   ├── routingMap.ts        # Leaflet integration
│   ├── notificacionesService.ts
│   └── tareasService.ts
│
├── config/
│   └── api.ts               # API endpoints constants
│
├── pages/
│   ├── ReportesPage.tsx
│   ├── OperadoresPage.tsx
│   ├── TrackingPage.tsx
│   └── HorariosPage.tsx
│
├── types/
│   └── index.ts             # TypeScript interfaces
│
└── utils/
    ├── auth.ts              # Auth helpers
    ├── formatting.ts        # Format utilities
    └── validation.ts        # Form validation
```

---

## TypeScript Interfaces

```typescript
// src/types/index.ts

// Domain Models
export interface Usuario {
  id: number;
  username: string;
  email: string;
  tipo_usuario: 'admin' | 'operador' | 'conductor';
  activo: boolean;
}

export interface Incidencia {
  id: number;
  tipo: 'acopio_lleno' | 'animal_muerto' | 'escombros' | 'zona_critica';
  gravedad: number;        // 1-10
  descripcion: string;
  foto_url?: string;
  lat: number;
  lon: number;
  zona: 'oriental' | 'occidental';
  estado: 'pendiente' | 'asignada' | 'resuelta';
  reportado_en: string;    // ISO datetime
}

export interface RutaGenerada {
  id: number;
  zona: 'oriental' | 'occidental';
  suma_gravedad: number;
  camiones_usados: number;
  costo_total: number;     // metros
  duracion_estimada: string;
  estado: 'planeada' | 'en_ejecucion' | 'completada';
  detalles: RutaDetalle[];
}

export interface RutaDetalle {
  id: number;
  orden: number;
  incidencia_id: number;
  lat: number;
  lon: number;
  tipo_punto: 'incidencia' | 'punto_fijo' | 'inicio' | 'fin';
  camion_tipo: string;
  camion_id?: string;
}

export interface Conductor {
  id: number;
  nombre_completo: string;
  cedula: string;
  telefono: string;
  licencia_tipo: string;
  estado: 'disponible' | 'ocupado' | 'inactivo';
  zona_preferida: 'oriental' | 'occidental' | 'ambas';
}

export interface AsignacionConductor {
  id: number;
  conductor_id: number;
  ruta_id: number;
  camion_id: string;
  camion_tipo: string;
  estado: 'asignada' | 'iniciada' | 'completada';
}

// API Request/Response
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  usuario_id: number;
  username: string;
}

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}
```

---

## Services

### Axios Configuration

```typescript
// src/services/apiService.ts

import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_BASE_URL } from '../config/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request Interceptor - agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor - manejar errores
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado - redirigir a login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Incidencias Service

```typescript
// src/services/incidenciasService.ts

import api from './apiService';
import { Incidencia } from '../types';

export const incidenciasService = {
  // Obtener todas las incidencias
  async obtenerTodas(): Promise<Incidencia[]> {
    const response = await api.get<Incidencia[]>('/incidencias/');
    return response.data;
  },

  // Obtener por zona
  async obtenerPorZona(zona: 'oriental' | 'occidental'): Promise<Incidencia[]> {
    const response = await api.get<Incidencia[]>(`/incidencias/zona/${zona}`);
    return response.data;
  },

  // Crear incidencia
  async crear(data: {
    tipo: string;
    gravedad: number;
    descripcion: string;
    lat: number;
    lon: number;
  }): Promise<Incidencia> {
    const response = await api.post<Incidencia>('/incidencias/', data);
    return response.data;
  },

  // Obtener estadísticas
  async obtenerEstadisticas(): Promise<{
    total_incidencias: number;
    pendientes: number;
    resueltas: number;
    tasa_resolucion: number;
  }> {
    const response = await api.get('/incidencias/stats');
    return response.data;
  }
};
```

### Rutas Service

```typescript
// src/services/rutasService.ts

import api from './apiService';
import { RutaGenerada, RutaDetalle } from '../types';

export const rutasService = {
  // Generar ruta optimizada
  async generarRuta(zona: 'oriental' | 'occidental'): Promise<RutaGenerada> {
    const response = await api.post<RutaGenerada>(
      `/rutas/generar/${zona}`
    );
    return response.data;
  },

  // Obtener ruta por ID
  async obtenerRuta(id: number): Promise<RutaGenerada> {
    const response = await api.get<RutaGenerada>(`/rutas/${id}`);
    return response.data;
  },

  // Obtener detalles de ruta
  async obtenerDetalles(rutaId: number): Promise<RutaDetalle[]> {
    const response = await api.get<RutaDetalle[]>(
      `/rutas/${rutaId}/detalles`
    );
    return response.data;
  },

  // Obtener rutas por zona
  async obtenerPorZona(zona: string): Promise<RutaGenerada[]> {
    const response = await api.get<RutaGenerada[]>(
      `/rutas/zona/${zona}`
    );
    return response.data;
  }
};
```

---

## Componentes Principales

### Dashboard

```typescript
// src/components/Dashboard/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import { Box, Grid, Card, CardContent, Typography } from '@mui/material';
import { incidenciasService } from '../../services/incidenciasService';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    total_incidencias: 0,
    pendientes: 0,
    resueltas: 0,
    tasa_resolucion: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      const data = await incidenciasService.obtenerEstadisticas();
      setStats(data);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Incidencias
              </Typography>
              <Typography variant="h5">
                {stats.total_incidencias}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pendientes
              </Typography>
              <Typography variant="h5" color="warning.main">
                {stats.pendientes}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Resueltas
              </Typography>
              <Typography variant="h5" color="success.main">
                {stats.resueltas}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Tasa de Resolución
              </Typography>
              <Typography variant="h5">
                {stats.tasa_resolucion}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
```

### Generación de Rutas

```typescript
// src/components/Routes/GeneracionRutas.tsx

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  Typography,
  Grid
} from '@mui/material';
import { rutasService } from '../../services/rutasService';
import { RutaGenerada } from '../../types';

const GeneracionRutas: React.FC = () => {
  const [zona, setZona] = useState<'oriental' | 'occidental'>('oriental');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ruta, setRuta] = useState<RutaGenerada | null>(null);

  const handleGenerar = async () => {
    setLoading(true);
    setError(null);
    setRuta(null);

    try {
      const resultado = await rutasService.generarRuta(zona);
      setRuta(resultado);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Error al generar ruta'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Generación Automática de Rutas
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
            <Select
              value={zona}
              onChange={(e) => setZona(e.target.value as any)}
              disabled={loading}
              sx={{ width: 200 }}
            >
              <MenuItem value="oriental">Zona Oriental</MenuItem>
              <MenuItem value="occidental">Zona Occidental</MenuItem>
            </Select>

            <Button
              variant="contained"
              onClick={handleGenerar}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Generar Ruta'}
            </Button>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {ruta && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">
                      Ruta #{ruta.id} Generada
                    </Typography>
                    <Typography>Zona: <strong>{ruta.zona}</strong></Typography>
                    <Typography>
                      Gravedad Total: <strong>{ruta.suma_gravedad}</strong>
                    </Typography>
                    <Typography>
                      Camiones: <strong>{ruta.camiones_usados}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">Métricas</Typography>
                    <Typography>
                      Distancia: <strong>{(ruta.costo_total / 1000).toFixed(2)} km</strong>
                    </Typography>
                    <Typography>
                      Duración: <strong>{ruta.duracion_estimada}</strong>
                    </Typography>
                    <Typography>
                      Estado: <strong>{ruta.estado}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default GeneracionRutas;
```

---

## Routing

```typescript
// src/App.tsx

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Login from './components/Auth/Login';
import DashboardLayout from './components/Layout/Dashboard';
import Dashboard from './components/Dashboard/Dashboard';
import IncidentsPage from './components/Incidents/IncidentsPage';
import RoutesPage from './components/Routes/RoutesPage';
import ReportsPage from './components/Reports/ReportsPage';
import { Usuario } from './types';

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [user, setUser] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Validar token con backend
      verificarAutenticacion();
    } else {
      setLoading(false);
    }
  }, []);

  const verificarAutenticacion = async () => {
    try {
      const response = await api.get<Usuario>('/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('access_token');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={!user ? <Login onLogin={setUser} /> : <Navigate to="/" />}
        />
        
        <Route
          path="/"
          element={user ? <DashboardLayout user={user} /> : <Navigate to="/login" />}
        >
          <Route index element={<Dashboard />} />
          <Route path="incidencias" element={<IncidentsPage />} />
          <Route path="rutas/*" element={<RoutesPage />} />
          <Route path="reportes" element={<ReportsPage />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
```

---

## Leaflet Integration

```typescript
// src/services/routingMap.ts

import L, { LatLngTuple } from 'leaflet';
import { RutaDetalle } from '../types';

export class RoutingMap {
  private map: L.Map | null = null;
  private markers: L.Marker[] = [];
  private polyline: L.Polyline | null = null;

  inicializar(elementId: string) {
    this.map = L.map(elementId).setView([0, 0], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 19
    }).addTo(this.map);
  }

  agregarMarker(
    lat: number,
    lon: number,
    label: string,
    orden?: number
  ): L.Marker {
    const icon = L.divIcon({
      html: `<div style="background: #2196F3; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">${orden || ''}</div>`,
      iconSize: [30, 30]
    });

    const marker = L.marker([lat, lon], { icon })
      .bindPopup(label)
      .addTo(this.map!);

    this.markers.push(marker);
    return marker;
  }

  dibujarRuta(detalles: RutaDetalle[]) {
    if (!this.map) return;

    // Extraer coordenadas en orden
    const coords: LatLngTuple[] = detalles.map(d => [d.lat, d.lon]);

    // Dibujar polyline
    this.polyline = L.polyline(coords, {
      color: '#2196F3',
      weight: 3,
      opacity: 0.8
    }).addTo(this.map);

    // Agregar marcadores
    detalles.forEach((detalle, idx) => {
      this.agregarMarker(
        detalle.lat,
        detalle.lon,
        `Punto ${detalle.orden}`,
        detalle.orden
      );
    });

    // Auto-zoom
    this.map.fitBounds(this.polyline.getBounds(), { padding: [50, 50] });
  }

  limpiar() {
    this.markers.forEach(m => m.remove());
    this.markers = [];
    if (this.polyline) this.polyline.remove();
  }
}

export const routingMap = new RoutingMap();
```

---

## Conclusión

El frontend de EPAGAL utiliza:
- ✅ React 18 con Hooks modernos
- ✅ TypeScript para type safety
- ✅ Material-UI para UI profesional
- ✅ Axios con interceptors
- ✅ Leaflet para mapeo
- ✅ Separación clara de concerns
- ✅ Componentes reutilizables
