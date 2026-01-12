import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export interface Tarea {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  created_at?: string;
}

export const listarTareas = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.TASKS.LISTAR);
    // Si es 404, devolver vacío (endpoint no existe)
    if (response.status === 404) {
      return { total: 0, tareas: [] };
    }
    const { data } = response;
    // Adaptar a estructura esperada por UI
    if (data && Array.isArray(data.tasks)) {
      return { total: data.total ?? data.tasks.length, tareas: data.tasks };
    }
    return { total: 0, tareas: [] };
  } catch (err: any) {
    // Errores reales (no 404)
    console.error('Error inesperado en listarTareas:', err);
    return { total: 0, tareas: [] };
  }
};

export const obtenerTarea = async (id: string | number) => {
  // Backend no expone GET /tasks/{id}; se filtra desde el listado
  const list = await listarTareas();
  return (list as any).tareas?.find((t: Tarea) => String(t.id) === String(id)) || null;
};

export const crearTarea = async (payload: Partial<Tarea>) => {
  const { data } = await api.post(API_ENDPOINTS.TASKS.CREAR, payload);
  return data;
};

export const actualizarTarea = async (id: string | number, payload: Partial<Tarea>) => {
  const { data } = await api.patch(API_ENDPOINTS.TASKS.ACTUALIZAR(id), payload);
  return data;
};

export const completarTarea = async (id: string | number) => {
  const { data } = await api.post(API_ENDPOINTS.TASKS.COMPLETAR(id));
  return data;
};

export default {
  listarTareas,
  obtenerTarea,
  crearTarea,
  actualizarTarea,
  completarTarea,
};
