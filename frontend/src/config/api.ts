// Configuración de la API
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login/`,
    REGISTER: `${API_BASE_URL}/auth/register/`,
    LOGOUT: `${API_BASE_URL}/auth/logout/`,
    REFRESH: `${API_BASE_URL}/auth/refresh/`,
    PROFILE: `${API_BASE_URL}/auth/profile/`,
  },
  // Incidentes
  INCIDENTS: `${API_BASE_URL}/incidents/`,
  // Rutas
  ROUTES: `${API_BASE_URL}/routes/`,
  ZONES: `${API_BASE_URL}/zones/`,
  // Tareas
  TASKS: `${API_BASE_URL}/tasks/`,
  // Notificaciones
  NOTIFICATIONS: `${API_BASE_URL}/notifications/`,
  // Reportes
  REPORTS: `${API_BASE_URL}/reports/`,
};

export default API_ENDPOINTS;
