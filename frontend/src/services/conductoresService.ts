import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

// ==================== CONDUCTORES CRUD ====================

export const listarConductores = async (params?: { skip?: number; limit?: number }) => {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.append('skip', String(params.skip));
  if (params?.limit !== undefined) query.append('limit', String(params.limit));
  const url = `${API_ENDPOINTS.CONDUCTORES.LISTAR}?${query.toString()}`;
  const { data } = await api.get(url);
  return data;
};

export const obtenerConductor = async (driverId: string | number) => {
  const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.OBTENER(driverId));
  return data;
};

export const crearConductor = async (payload: any) => {
  const { data } = await api.post(API_ENDPOINTS.CONDUCTORES.CREAR, payload);
  return data;
};

export const actualizarConductor = async (driverId: string | number, payload: any) => {
  const { data } = await api.patch(API_ENDPOINTS.CONDUCTORES.ACTUALIZAR(driverId), payload);
  return data;
};

export const eliminarConductor = async (driverId: string | number) => {
  await api.delete(API_ENDPOINTS.CONDUCTORES.ELIMINAR(driverId));
};

// ==================== RUTAS DEL CONDUCTOR ====================

export const misRutasTodas = async () => {
  const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.MIS_RUTAS_TODAS);
  return data;
};

export const miRutaActual = async () => {
  const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.MIS_RUTAS_ACTUAL);
  return data;
};

export default {
  listarConductores,
  obtenerConductor,
  crearConductor,
  actualizarConductor,
  eliminarConductor,
  misRutasTodas,
  miRutaActual,
};

