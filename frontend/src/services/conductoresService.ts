import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export const misRutasTodas = async (estado?: string) => {
  const url = API_ENDPOINTS.CONDUCTORES.MIS_RUTAS_TODAS + (estado ? `?estado=${estado}` : '');
  const { data } = await api.get(url);
  return data; // { total, asignado, iniciado, completado, rutas: [] }
};

export const miRutaActual = async () => {
  const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.MIS_RUTAS_ACTUAL);
  return data; // { message, ruta_actual }
};

export const iniciarRuta = async (rutaId: number) => {
  const { data } = await api.post(API_ENDPOINTS.CONDUCTORES.INICIAR_RUTA, { ruta_id: rutaId });
  return data; // { message, asignacion_id, ruta_id, fecha_inicio, estado }
};

export const finalizarRuta = async (rutaId: number, notas?: string) => {
  const { data } = await api.post(API_ENDPOINTS.CONDUCTORES.FINALIZAR_RUTA, { ruta_id: rutaId, notas });
  return data; // { message, asignacion_id, ruta_id, fecha_finalizacion, estado }
};

export const asignacionesPorRuta = async (rutaId: number) => {
  const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.ASIGNACIONES_RUTA(rutaId));
  return data; // Lista de asignaciones
};

export default {
  misRutasTodas,
  miRutaActual,
  iniciarRuta,
  finalizarRuta,
  asignacionesPorRuta,
};
