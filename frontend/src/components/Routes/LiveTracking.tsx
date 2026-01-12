import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  GpsFixed as GpsIcon,
  Speed as SpeedIcon,
  LocalShipping as TruckIcon,
  Person as PersonIcon,
  Place as PlaceIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../../services/apiService';
import { API_BASE_URL } from '../../config/api';

// Configurar icono de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface TrackingData {
  ejecucion_id: number;
  conductor_nombre: string;
  camion_placa: string;
  sector: string;
  lat: number;
  lon: number;
  velocidad: number | null;
  timestamp: string;
  estado: string;
}

interface TrackingPoint {
  lat: number;
  lon: number;
  velocidad: number | null;
  timestamp: string;
}

interface WebSocketMessage {
  type: string;
  ejecucion_id: number;
  lat: number;
  lon: number;
  velocidad: number | null;
  timestamp: string;
}

const LiveTracking: React.FC = () => {
  const [activeTracking, setActiveTracking] = useState<TrackingData[]>([]);
  const [selectedTracking, setSelectedTracking] = useState<TrackingData | null>(null);
  const [routeHistory, setRouteHistory] = useState<TrackingPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const mapRef = useRef<any>(null);

  // Cargar tracking activos al montar
  useEffect(() => {
    loadActiveTracking();
    const interval = setInterval(loadActiveTracking, 30000); // Actualizar cada 30s
    return () => clearInterval(interval);
  }, []);

  // Conectar WebSocket cuando se selecciona un tracking
  useEffect(() => {
    if (selectedTracking) {
      connectWebSocket(selectedTracking.ejecucion_id);
      loadRouteHistory(selectedTracking.ejecucion_id);
    }
    return () => {
      disconnectWebSocket();
    };
  }, [selectedTracking]);

  const loadActiveTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/tracking/activos');
      setActiveTracking(response.data);
      
      // Si hay tracking activos y no hay uno seleccionado, seleccionar el primero
      if (response.data.length > 0 && !selectedTracking) {
        setSelectedTracking(response.data[0]);
      }
    } catch (err: any) {
      console.error('Error loading active tracking:', err);
      setError(err.response?.data?.detail || 'Error al cargar tracking activo');
    } finally {
      setLoading(false);
    }
  };

  const loadRouteHistory = async (ejecucionId: number) => {
    try {
      const response = await api.get(`/tracking/ruta/${ejecucionId}`);
      setRouteHistory(response.data.puntos || []);
    } catch (err: any) {
      console.error('Error loading route history:', err);
    }
  };

  const connectWebSocket = (ejecucionId: number) => {
    disconnectWebSocket();

    const wsUrl = `${API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/tracking/ws/${ejecucionId}`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        setError(null);
        
        // Enviar ping cada 30s para mantener conexión
        const pingInterval = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send('ping');
          }
        }, 30000);
        
        // Guardar interval para limpiarlo después
        (wsRef.current as any).pingInterval = pingInterval;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'position_update') {
            // Actualizar posición en tiempo real
            setSelectedTracking(prev => {
              if (prev && prev.ejecucion_id === message.ejecucion_id) {
                return {
                  ...prev,
                  lat: message.lat,
                  lon: message.lon,
                  velocidad: message.velocidad,
                  timestamp: message.timestamp,
                };
              }
              return prev;
            });

            // Agregar punto al historial
            setRouteHistory(prev => [
              ...prev,
              {
                lat: message.lat,
                lon: message.lon,
                velocidad: message.velocidad,
                timestamp: message.timestamp,
              },
            ]);

            // Centrar mapa en nueva posición
            if (mapRef.current) {
              mapRef.current.setView([message.lat, message.lon], 15);
            }
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Error en la conexión WebSocket');
        setWsConnected(false);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        
        // Limpiar interval de ping
        if ((wsRef.current as any)?.pingInterval) {
          clearInterval((wsRef.current as any).pingInterval);
        }
      };
    } catch (err) {
      console.error('Error connecting WebSocket:', err);
      setError('No se pudo conectar al sistema de tracking');
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      if ((wsRef.current as any).pingInterval) {
        clearInterval((wsRef.current as any).pingInterval);
      }
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-EC', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatSpeed = (speed: number | null) => {
    return speed !== null ? `${speed.toFixed(1)} km/h` : 'N/A';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <GpsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Tracking en Tiempo Real
        </Typography>
        <Chip
          icon={wsConnected ? <GpsIcon /> : <RefreshIcon />}
          label={wsConnected ? 'Conectado' : 'Desconectado'}
          color={wsConnected ? 'success' : 'default'}
          size="small"
        />
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
      ) : activeTracking.length === 0 ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Vehículos Activos (0)
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                No hay vehículos en ruta actualmente
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={9}>
            <Paper sx={{ p: 2, height: 600 }}>
              <Typography variant="h6" gutterBottom>
                Mapa (sin datos en tiempo real)
              </Typography>
              <MapContainer
                center={[-0.9326, -78.6139]}
                zoom={13}
                style={{ height: '540px', width: '100%' }}
                ref={mapRef}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
              </MapContainer>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Grid container spacing={3}>
          {/* Lista de vehículos activos */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Vehículos Activos ({activeTracking.length})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                {activeTracking.map((tracking) => (
                  <ListItem
                    key={tracking.ejecucion_id}
                    button
                    selected={selectedTracking?.ejecucion_id === tracking.ejecucion_id}
                    onClick={() => setSelectedTracking(tracking)}
                  >
                    <ListItemIcon>
                      <TruckIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={tracking.camion_placa}
                      secondary={tracking.sector}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Detalles del vehículo seleccionado */}
          <Grid item xs={12} md={9}>
            {selectedTracking && (
              <>
                {/* Información del vehículo */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <TruckIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            Vehículo
                          </Typography>
                        </Box>
                        <Typography variant="h6">
                          {selectedTracking.camion_placa}
                        </Typography>
                      </Grid>

                      <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            Conductor
                          </Typography>
                        </Box>
                        <Typography variant="body1">
                          {selectedTracking.conductor_nombre}
                        </Typography>
                      </Grid>

                      <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <PlaceIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            Sector
                          </Typography>
                        </Box>
                        <Typography variant="body1">
                          {selectedTracking.sector}
                        </Typography>
                      </Grid>

                      <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <SpeedIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            Velocidad
                          </Typography>
                        </Box>
                        <Typography variant="h6" color="primary">
                          {formatSpeed(selectedTracking.velocidad)}
                        </Typography>
                      </Grid>

                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">
                          Última actualización: {formatTimestamp(selectedTracking.timestamp)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* Mapa con tracking */}
                <Paper sx={{ p: 2, height: 600 }}>
                  <Typography variant="h6" gutterBottom>
                    Ubicación en Tiempo Real
                  </Typography>
                  <MapContainer
                    center={[selectedTracking.lat, selectedTracking.lon]}
                    zoom={15}
                    style={{ height: '540px', width: '100%' }}
                    ref={mapRef}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    />
                    
                    {/* Ruta recorrida */}
                    {routeHistory.length > 0 && (
                      <Polyline
                        positions={routeHistory.map(p => [p.lat, p.lon])}
                        color="#2196f3"
                        weight={3}
                        opacity={0.6}
                      />
                    )}
                    
                    {/* Posición actual */}
                    <Marker position={[selectedTracking.lat, selectedTracking.lon]}>
                      <Popup>
                        <strong>{selectedTracking.camion_placa}</strong>
                        <br />
                        Conductor: {selectedTracking.conductor_nombre}
                        <br />
                        Velocidad: {formatSpeed(selectedTracking.velocidad)}
                        <br />
                        {formatTimestamp(selectedTracking.timestamp)}
                      </Popup>
                    </Marker>
                  </MapContainer>
                </Paper>
              </>
            )}
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default LiveTracking;
