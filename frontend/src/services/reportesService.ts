import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export interface ReporteEstadisticas {
  total_incidencias: number;
  incidencias_por_estado: Record<string, number>;
  incidencias_por_tipo: Record<string, number>;
  total_rutas?: number;
  por_zona?: Record<string, number>;
}

export const reporteEstadisticas = async (params?: { fecha_inicio?: string; fecha_fin?: string; }) => {
  try {
    // El endpoint /incidencias/stats no requiere parámetros de fecha (trae todo)
    // pero los aceptamos para compatibilidad con el frontend
    const response = await api.get(`${API_ENDPOINTS.INCIDENCIAS.STATS}`);
    
    if (response.status === 404) {
      return {
        total_incidencias: 0,
        incidencias_por_estado: {},
        incidencias_por_tipo: {},
        total_rutas: 0,
      } as ReporteEstadisticas;
    }
    
    const { data } = response;
    return {
      total_incidencias: data.total || 0,
      incidencias_por_estado: data.por_estado || {},
      incidencias_por_tipo: data.por_tipo || {},
      total_rutas: 0,
      por_zona: data.por_zona || {},
    } as ReporteEstadisticas;
  } catch (err: any) {
    console.error('Error en reporteEstadisticas:', err);
    return {
      total_incidencias: 0,
      incidencias_por_estado: {},
      incidencias_por_tipo: {},
      total_rutas: 0,
    } as ReporteEstadisticas;
  }
};

export const exportarReporte = async (formato: 'pdf' | 'excel') => {
  const { data } = await api.post(API_ENDPOINTS.REPORTS.EXPORTAR, { format: formato });
  return data;
};

export default {
  reporteEstadisticas,
  exportarReporte,
};
