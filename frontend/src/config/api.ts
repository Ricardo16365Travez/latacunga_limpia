// Configuración de API - Backend único FastAPI en Render
// Backend: https://epagal-backend-routing-latest.onrender.com
// Documentación: https://epagal-backend-routing-latest.onrender.com/docs
// Este backend maneja: incidencias, rutas, conductores, auth, tareas, notificaciones, reportes

// Normaliza la base para evitar errores si la env incluye /api o /api/v1
const normalizeBase = (raw?: string) => {
  const fallback = 'https://epagal-backend-routing-latest.onrender.com';
  if (!raw) return fallback;
  let base = raw.trim();
  base = base.replace(/\/api(?:\/v1)?$/i, '');
  base = base.replace(/\/+$/g, '');
  return base || fallback;
};

// URL base única del backend
const API_BASE = normalizeBase(
  process.env.REACT_APP_API_BASE || 'https://epagal-backend-routing-latest.onrender.com'
);
const API_PREFIX = '/api';
const API_V1 = API_PREFIX;

export const API_BASE_URL = `${API_BASE}${API_PREFIX}`;

export const API_ENDPOINTS = {
  // ==================== AUTENTICACIÓN ====================
  AUTH: {
    LOGIN: `${API_BASE}${API_V1}/auth/login`,
    LOGOUT: `${API_BASE}${API_V1}/auth/logout`,
    ME: `${API_BASE}${API_V1}/auth/me`,
  },

  // ==================== CONDUCTORES ====================
  CONDUCTORES: {
    LISTAR: `${API_BASE}${API_V1}/conductores/`,
    CREAR: `${API_BASE}${API_V1}/conductores/`,
    OBTENER: (id: string | number) => `${API_BASE}${API_V1}/conductores/${id}`,
    ACTUALIZAR: (id: string | number) => `${API_BASE}${API_V1}/conductores/${id}`,
    ELIMINAR: (id: string | number) => `${API_BASE}${API_V1}/conductores/${id}`,
    MIS_RUTAS_TODAS: `${API_BASE}${API_V1}/conductores/mis-rutas/todas`,
    MIS_RUTAS_ACTUAL: `${API_BASE}${API_V1}/conductores/mis-rutas/actual`,
  },

  // ==================== INCIDENTES ====================
  INCIDENCIAS: {
    LISTAR: `${API_BASE}${API_V1}/incidencias/`,
    CREAR: `${API_BASE}${API_V1}/incidencias/`,
    OBTENER: (id: string | number) => `${API_BASE}${API_V1}/incidencias/${id}`,
    ACTUALIZAR: (id: string | number) => `${API_BASE}${API_V1}/incidencias/${id}`,
    ELIMINAR: (id: string | number) => `${API_BASE}${API_V1}/incidencias/${id}`,
    STATS: `${API_BASE}${API_V1}/incidencias/stats`,
  },

  // ==================== RUTAS ====================
  RUTAS: {
    LISTAR: `${API_BASE}${API_V1}/rutas/`,
    CREAR: `${API_BASE}${API_V1}/rutas/`,
    OBTENER: (id: string | number) => `${API_BASE}${API_V1}/rutas/${id}`,
    ACTUALIZAR: (id: string | number) => `${API_BASE}${API_V1}/rutas/${id}`,
    ELIMINAR: (id: string | number) => `${API_BASE}${API_V1}/rutas/${id}`,
    POR_ZONA: (zona: string) => `${API_BASE}${API_V1}/rutas/zona/${zona}`,
  },

  // ==================== TAREAS ====================
  TASKS: {
    LISTAR: `${API_BASE}${API_V1}/tasks/`,
    CREAR: `${API_BASE}${API_V1}/tasks/`,
    ACTUALIZAR: (id: string | number) => `${API_BASE}${API_V1}/tasks/${id}`,
    COMPLETAR: (id: string | number) => `${API_BASE}${API_V1}/tasks/${id}/complete`,
  },

  // ==================== NOTIFICACIONES ====================
  NOTIFICATIONS: {
    LISTAR: `${API_BASE}${API_V1}/notifications/`,
    LEER: (id: string | number) => `${API_BASE}${API_V1}/notifications/${id}/read`,
    LEER_TODAS: `${API_BASE}${API_V1}/notifications/read-all`,
  },

  // ==================== REPORTES ====================
  REPORTS: {
    ESTADISTICAS: `${API_BASE}${API_V1}/reports/statistics/`,
    EXPORTAR: `${API_BASE}${API_V1}/reports/export/`,
  },
};

export default API_ENDPOINTS;
