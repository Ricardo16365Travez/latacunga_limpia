// Configuración de la API (FastAPI externo)
// Por defecto apunta al backend en Render
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://epagal-backend-routing-latest.onrender.com/api';

export const API_ENDPOINTS = {
  // Autenticación (JWT)
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
    ME: `${API_BASE_URL}/auth/me`,
    VERIFY: `${API_BASE_URL}/auth/verify-token`,
  },
  // Conductores
  CONDUCTORES: {
    MIS_RUTAS_TODAS: `${API_BASE_URL}/conductores/mis-rutas/todas`,
    MIS_RUTAS_ACTUAL: `${API_BASE_URL}/conductores/mis-rutas/actual`,
    INICIAR_RUTA: `${API_BASE_URL}/conductores/iniciar-ruta`,
    FINALIZAR_RUTA: `${API_BASE_URL}/conductores/finalizar-ruta`,
    ASIGNACIONES_RUTA: (rutaId: number) => `${API_BASE_URL}/conductores/asignaciones/ruta/${rutaId}`,
  },
  // Rutas
  RUTAS: {
    GENERAR: (zona: string) => `${API_BASE_URL}/rutas/generar/${zona}`,
    OBTENER: (rutaId: number) => `${API_BASE_URL}/rutas/${rutaId}`,
    DETALLES: (rutaId: number) => `${API_BASE_URL}/rutas/${rutaId}/detalles`,
    POR_ZONA: (zona: string) => `${API_BASE_URL}/rutas/zona/${zona}`,
  },
  // Incidencias
  INCIDENCIAS: {
    LISTAR: `${API_BASE_URL}/incidencias/`,
    CREAR: `${API_BASE_URL}/incidencias/`,
    STATS: `${API_BASE_URL}/incidencias/stats`,
    OBTENER: (id: number) => `${API_BASE_URL}/incidencias/${id}`,
    ACTUALIZAR: (id: number) => `${API_BASE_URL}/incidencias/${id}`,
    ELIMINAR: (id: number) => `${API_BASE_URL}/incidencias/${id}`,
  },
};

export default API_ENDPOINTS;
