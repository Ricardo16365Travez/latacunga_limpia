import api from './apiService';
import { API_ENDPOINTS } from '../config/api';

export interface Notificacion {
  id: number;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

export const listarNotificaciones = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.NOTIFICATIONS.LISTAR);
    // Si es 404, devolver vacío (endpoint no existe)
    if (response.status === 404) {
      return { total: 0, unread: 0, notificaciones: [] };
    }
    const { data } = response;
    if (data && Array.isArray(data.notifications)) {
      return { total: data.total ?? data.notifications.length, unread: data.unread ?? 0, notificaciones: data.notifications };
    }
    return { total: 0, unread: 0, notificaciones: [] };
  } catch (err: any) {
    // Errores reales (no 404)
    console.error('Error inesperado en listarNotificaciones:', err);
    return { total: 0, unread: 0, notificaciones: [] };
  }
};

export const marcarComoLeida = async (id: string | number) => {
  try {
    const { data } = await api.patch(API_ENDPOINTS.NOTIFICATIONS.LEER(id), {});
    return data;
  } catch {
    return null;
  }
};

export const marcarTodasLeidas = async () => {
  try {
    const { data } = await api.post(API_ENDPOINTS.NOTIFICATIONS.LEER_TODAS, {});
    return data;
  } catch {
    return null;
  }
};

export default {
  listarNotificaciones,
  marcarComoLeida,
  marcarTodasLeidas,
};
