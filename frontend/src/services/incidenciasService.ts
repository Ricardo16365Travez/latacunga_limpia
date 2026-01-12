import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export const listarIncidencias = async (params?: { estado?: string; zona?: string; tipo?: string; skip?: number; limit?: number; }) => {
  const query = new URLSearchParams();
  if (params?.estado) query.append('estado', params.estado);
  if (params?.zona) query.append('zona', params.zona);
  if (params?.tipo) query.append('tipo', params.tipo);
  // Defaults para asegurar que se carguen varias incidencias
  const skip = params?.skip ?? 0;
  const limit = params?.limit ?? 100;
  query.append('skip', String(skip));
  query.append('limit', String(limit));
  const url = `${API_ENDPOINTS.INCIDENCIAS.LISTAR}?${query.toString()}`;
  const { data } = await api.get(url);
  return data;
};

export const crearIncidencia = async (payload: any, autoGenerarRuta = false) => {
  const url = `${API_ENDPOINTS.INCIDENCIAS.CREAR}?auto_generar_ruta=${autoGenerarRuta}`;
  const { data } = await api.post(url, payload);
  return data;
};

export const obtenerIncidencia = async (id: string | number) => {
  const { data } = await api.get(API_ENDPOINTS.INCIDENCIAS.OBTENER(id));
  return data;
};

export const actualizarIncidencia = async (id: string | number, payload: any) => {
  const { data } = await api.patch(API_ENDPOINTS.INCIDENCIAS.ACTUALIZAR(id), payload);
  return data;
};

export const eliminarIncidencia = async (id: string | number) => {
  await api.delete(API_ENDPOINTS.INCIDENCIAS.ELIMINAR(id));
};

export const estadisticasIncidencias = async () => {
  const { data } = await api.get(API_ENDPOINTS.INCIDENCIAS.STATS);
  return data;
};

export const verificarUmbralZona = async (zona: string) => {
  // Backend actual no expone umbrales
  // Devolver estructura vacía para que no cause errores
  return {
    zona,
    suma_gravedad: 0,
    umbral_configurado: 999,
    incidencias_pendientes: 0,
    debe_generar_ruta: false,
  };
};

const IncidenciasService = {
  listarIncidencias,
  crearIncidencia,
  obtenerIncidencia,
  actualizarIncidencia,
  eliminarIncidencia,
  estadisticasIncidencias,
  verificarUmbralZona,
};

export default IncidenciasService;
