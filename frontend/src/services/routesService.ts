import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export const generarRuta = async (zona: string) => {
  const { data } = await api.post(API_ENDPOINTS.RUTAS.GENERAR(zona));
  return data;
};

export const obtenerRuta = async (rutaId: number) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.OBTENER(rutaId));
  return data; // { id, zona, puntos[], polyline? }
};

export const obtenerDetallesRuta = async (rutaId: number) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.DETALLES(rutaId));
  return data; // { ruta, incidencias[], puntos[] }
};

export const listarRutasPorZona = async (zona: string) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.POR_ZONA(zona));
  return data; // { total, rutas: [] }
};

export default {
  generarRuta,
  obtenerRuta,
  obtenerDetallesRuta,
  listarRutasPorZona,
};
