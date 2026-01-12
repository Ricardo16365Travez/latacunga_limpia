import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

// Rutas - CRUD expuesto por FastAPI

export const listarRutas = async (params?: { skip?: number; limit?: number }) => {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.append('skip', String(params.skip));
  if (params?.limit !== undefined) query.append('limit', String(params.limit));
  const url = `${API_ENDPOINTS.RUTAS.LISTAR}?${query.toString()}`;
  const { data } = await api.get(url);
  return data;
};

export const obtenerRuta = async (routeId: string | number) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.OBTENER(routeId));
  return data;
};

export const crearRuta = async (payload: any) => {
  const { data } = await api.post(API_ENDPOINTS.RUTAS.CREAR, payload);
  return data;
};

export const actualizarRuta = async (routeId: string | number, payload: any) => {
  const { data } = await api.patch(API_ENDPOINTS.RUTAS.ACTUALIZAR(routeId), payload);
  return data;
};

export const eliminarRuta = async (routeId: string | number) => {
  await api.delete(API_ENDPOINTS.RUTAS.ELIMINAR(routeId));
};

export const rutasPorZona = async (zona: string) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.POR_ZONA(zona));
  return data;
};

export default {
  listarRutas,
  obtenerRuta,
  crearRuta,
  actualizarRuta,
  eliminarRuta,
  rutasPorZona,
};
