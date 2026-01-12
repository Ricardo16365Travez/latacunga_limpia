import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Badge,
  Box,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Delete as DeleteIcon,
  MarkEmailRead as ReadIcon,
} from '@mui/icons-material';
import notificationsService from '../../services/notificacionesService';
import { toErrorMessage } from '../../services/errorUtils';

interface Notification {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  leida: boolean;
  prioridad?: string;
  created_at?: string;
  metadata?: any;
}

const NOTIFICATION_TYPES = {
  INFO: { icon: InfoIcon, color: '#2196f3', label: 'Información' },
  SUCCESS: { icon: SuccessIcon, color: '#4caf50', label: 'Éxito' },
  WARNING: { icon: WarningIcon, color: '#ff9800', label: 'Advertencia' },
  ERROR: { icon: ErrorIcon, color: '#f44336', label: 'Error' },
};

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  useEffect(() => {
    loadNotifications();
    
    // Polling cada 30 segundos
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      // Usa baseURL con prefijo /api y estructura del backend FastAPI
      const data = await notificationsService.listarNotificaciones();
      setNotifications((data.notificaciones || []) as any);
    } catch (err: any) {
      setError(toErrorMessage(err) || 'Error al cargar notificaciones');
      console.error('Error loading notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id: number) => {
    const res = await notificationsService.marcarComoLeida(id);
    if (!res) setError('Marcar notificaciones no está disponible en el backend actual.');
  };

  const handleMarkAllAsRead = async () => {
    const res = await notificationsService.marcarTodasLeidas();
    if (!res) setError('Marcar todas como leídas no está disponible en el backend actual.');
  };

  const handleDelete = async (id: number) => {
    setError('Eliminar notificaciones no está disponible en el backend actual.');
  };

  const getNotificationIcon = (tipo: string) => {
    const config = NOTIFICATION_TYPES[tipo as keyof typeof NOTIFICATION_TYPES];
    if (!config) return { icon: InfoIcon, color: '#757575' };
    return config;
  };

  const formatTime = (date: string) => {
    const now = new Date();
    const notifDate = new Date(date);
    const diff = now.getTime() - notifDate.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Hace un momento';
    if (minutes < 60) return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    if (days < 7) return `Hace ${days} día${days > 1 ? 's' : ''}`;
    
    return notifDate.toLocaleDateString('es-EC', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const filteredNotifications = notifications.filter(notif => 
    filter === 'all' || !notif.leida
  );

  const unreadCount = notifications.filter(n => !n.leida).length;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <Badge badgeContent={unreadCount} color="error" sx={{ mr: 2 }}>
            <NotificationsIcon sx={{ verticalAlign: 'middle' }} />
          </Badge>
          Notificaciones
        </Typography>
        <Box>
          <Button
            variant={filter === 'all' ? 'contained' : 'outlined'}
            onClick={() => setFilter('all')}
            sx={{ mr: 1 }}
          >
            Todas
          </Button>
          <Button
            variant={filter === 'unread' ? 'contained' : 'outlined'}
            onClick={() => setFilter('unread')}
            sx={{ mr: 2 }}
          >
            No leídas ({unreadCount})
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadNotifications}
            sx={{ mr: 2 }}
          >
            Actualizar
          </Button>
          {unreadCount > 0 && (
            <Button
              variant="outlined"
              startIcon={<ReadIcon />}
              onClick={handleMarkAllAsRead}
            >
              Marcar todas leídas
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper>
          {filteredNotifications.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {filter === 'unread' 
                  ? 'No tienes notificaciones sin leer' 
                  : 'No hay notificaciones'}
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredNotifications.map((notification, index) => {
                const iconConfig = getNotificationIcon(notification.tipo);
                const Icon = iconConfig.icon;

                return (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      sx={{
                        bgcolor: notification.leida ? 'transparent' : 'action.hover',
                        '&:hover': {
                          bgcolor: 'action.selected',
                        },
                      }}
                      secondaryAction={
                        <Box>
                          {!notification.leida && (
                            <IconButton
                              edge="end"
                              onClick={() => handleMarkAsRead(notification.id)}
                              sx={{ mr: 1 }}
                            >
                              <ReadIcon />
                            </IconButton>
                          )}
                          <IconButton
                            edge="end"
                            onClick={() => handleDelete(notification.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: iconConfig.color }}>
                          <Icon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                              variant="subtitle1"
                              component="span"
                              sx={{ fontWeight: notification.leida ? 'normal' : 'bold' }}
                            >
                              {notification.titulo}
                            </Typography>
                            {notification.prioridad === 'ALTA' && (
                              <Chip label="Alta prioridad" size="small" color="error" />
                            )}
                            {!notification.leida && (
                              <Chip label="Nueva" size="small" color="primary" />
                            )}
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography
                              variant="body2"
                              color="text.primary"
                              component="span"
                              display="block"
                              sx={{ mt: 0.5 }}
                            >
                              {notification.mensaje}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              component="span"
                              display="block"
                              sx={{ mt: 0.5 }}
                            >
                              {formatTime(notification.created_at || new Date().toISOString())}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                    {index < filteredNotifications.length - 1 && <Divider component="li" />}
                  </React.Fragment>
                );
              })}
            </List>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default NotificationsPage;
