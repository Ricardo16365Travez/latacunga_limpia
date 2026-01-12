import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export const listarRutas = async (params?: { zona?: string; estado?: string; skip?: number; limit?: number; }) => {
  // Si no se especifica zona, intentar ambas zonas
  const zona = params?.zona || 'oriental';
  
  try {
    const { data } = await api.get(API_ENDPOINTS.RUTAS.POR_ZONA(zona));
    // El backend retorna { zona, total, rutas }
    return data.rutas || [];
  } catch (error) {
    console.error('Error al listar rutas:', error);
    return [];
  }
};

export const crearRuta = async (payload: any) => {
  const { data } = await api.post(API_ENDPOINTS.RUTAS.CREAR, payload);
  return data;
};

export const obtenerRuta = async (id: string | number) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.OBTENER(id));
  return data;
};

export const actualizarRuta = async (id: string | number, payload: any) => {
  const { data } = await api.patch(API_ENDPOINTS.RUTAS.ACTUALIZAR(id), payload);
  return data;
};

export const eliminarRuta = async (id: string | number) => {
  await api.delete(API_ENDPOINTS.RUTAS.ELIMINAR(id));
};

export const obtenerRutasPorZona = async (zona: string) => {
  const { data } = await api.get(API_ENDPOINTS.RUTAS.POR_ZONA(zona));
  return data;
};

const RutasService = {
  listarRutas,
  crearRuta,
  obtenerRuta,
  actualizarRuta,
  eliminarRuta,
  obtenerRutasPorZona,
};

export default RutasService;
