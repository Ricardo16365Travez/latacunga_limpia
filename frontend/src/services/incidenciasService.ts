import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export const listarIncidencias = async (params?: { estado?: string; zona?: string; tipo?: string; skip?: number; limit?: number; }) => {
  const query = new URLSearchParams();
  if (params?.estado) query.append('estado', params.estado);
  if (params?.zona) query.append('zona', params.zona);
  if (params?.tipo) query.append('tipo', params.tipo);
  if (params?.skip !== undefined) query.append('skip', String(params.skip));
  if (params?.limit !== undefined) query.append('limit', String(params.limit));
  const { data } = await api.get(`${API_ENDPOINTS.INCIDENCIAS.LISTAR}?${query.toString()}`);
  return data;
};

export const crearIncidencia = async (payload: any, autoGenerarRuta = false) => {
  const { data } = await api.post(`${API_ENDPOINTS.INCIDENCIAS.CREAR}?auto_generar_ruta=${autoGenerarRuta}`, payload);
  return data;
};

export const obtenerIncidencia = async (id: number) => {
  const { data } = await api.get(API_ENDPOINTS.INCIDENCIAS.OBTENER(id));
  return data;
};

export const actualizarIncidencia = async (id: number, payload: any) => {
  const { data } = await api.patch(API_ENDPOINTS.INCIDENCIAS.ACTUALIZAR(id), payload);
  return data;
};

export const eliminarIncidencia = async (id: number) => {
  await api.delete(API_ENDPOINTS.INCIDENCIAS.ELIMINAR(id));
};

export const estadisticasIncidencias = async () => {
  const { data } = await api.get(API_ENDPOINTS.INCIDENCIAS.STATS);
  return data;
};

export default {
  listarIncidencias,
  crearIncidencia,
  obtenerIncidencia,
  actualizarIncidencia,
  eliminarIncidencia,
  estadisticasIncidencias,
};
