import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Route as RouteIcon,
  LocalShipping as TruckIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../../services/apiService';

interface Route {
  id: number;
  nombre: string;
  descripcion: string;
  estado: string;
  tipo_ruta: string;
  vehiculo?: {
    placa: string;
    tipo: string;
  };
  conductor?: {
    display_name: string;
  };
  puntos_ruta: {
    type: string;
    coordinates: number[][];
  };
  distancia_km?: number;
  duracion_estimada?: number;
  hora_inicio?: string;
  hora_fin?: string;
  created_at: string;
}

interface Zone {
  id: number;
  nombre: string;
  tipo: string;
}

const ROUTE_TYPES = [
  { value: 'RESIDENCIAL', label: 'Residencial' },
  { value: 'COMERCIAL', label: 'Comercial' },
  { value: 'INDUSTRIAL', label: 'Industrial' },
  { value: 'MIXTA', label: 'Mixta' },
];

const ROUTE_STATUS = [
  { value: 'PLANIFICADA', label: 'Planificada', color: '#757575' },
  { value: 'EN_PROGRESO', label: 'En Progreso', color: '#2196f3' },
  { value: 'COMPLETADA', label: 'Completada', color: '#4caf50' },
  { value: 'CANCELADA', label: 'Cancelada', color: '#f44336' },
];

const RoutesPage: React.FC = () => {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    tipo_ruta: 'RESIDENCIAL',
    zona_id: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [routesRes, zonesRes] = await Promise.all([
        api.get('/routes/'),
        api.get('/zones/'),
      ]);
      setRoutes(routesRes.data.results || routesRes.data);
      setZones(zonesRes.data.results || zonesRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar datos');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoute = async () => {
    try {
      await api.post('/routes/', formData);
      setOpenDialog(false);
      resetForm();
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear ruta');
    }
  };

  const handleOptimizeRoute = async (id: number) => {
    try {
      await api.post(`/routes/${id}/optimize/`);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al optimizar ruta');
    }
  };

  const handleUpdateStatus = async (id: number, estado: string) => {
    try {
      await api.patch(`/routes/${id}/`, { estado });
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar estado');
    }
  };

  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
      tipo_ruta: 'RESIDENCIAL',
      zona_id: '',
    });
  };

  const getStatusColor = (estado: string) => {
    return ROUTE_STATUS.find(s => s.value === estado)?.color || '#757575';
  };

  const formatTime = (time?: string) => {
    if (!time) return 'N/A';
    return new Date(time).toLocaleTimeString('es-EC', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <RouteIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Gestión de Rutas
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadData}
            sx={{ mr: 2 }}
          >
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Nueva Ruta
          </Button>
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
        <>
          {/* Mapa de Rutas */}
          <Paper sx={{ p: 2, mb: 3, height: 500 }}>
            <Typography variant="h6" gutterBottom>
              Mapa de Rutas
            </Typography>
            <MapContainer
              center={[-0.9346, -78.6156]}
              zoom={13}
              style={{ height: '450px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              />
              {routes.map((route) => {
                if (!route.puntos_ruta?.coordinates) return null;
                
                const positions = route.puntos_ruta.coordinates.map(
                  coord => [coord[1], coord[0]] as [number, number]
                );

                const color = getStatusColor(route.estado);

                return (
                  <React.Fragment key={route.id}>
                    <Polyline
                      positions={positions}
                      color={color}
                      weight={4}
                      opacity={0.7}
                    />
                    {positions[0] && (
                      <Marker position={positions[0]}>
                        <Popup>
                          <strong>{route.nombre}</strong>
                          <br />
                          Tipo: {ROUTE_TYPES.find(t => t.value === route.tipo_ruta)?.label}
                          <br />
                          Distancia: {route.distancia_km?.toFixed(2)} km
                          <br />
                          Estado: {ROUTE_STATUS.find(s => s.value === route.estado)?.label}
                        </Popup>
                      </Marker>
                    )}
                  </React.Fragment>
                );
              })}
            </MapContainer>
          </Paper>

          {/* Lista de Rutas */}
          <Grid container spacing={3}>
            {routes.map((route) => (
              <Grid item xs={12} md={6} key={route.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        {route.nombre}
                      </Typography>
                      <Chip
                        label={ROUTE_STATUS.find(s => s.value === route.estado)?.label}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(route.estado),
                          color: 'white',
                        }}
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {route.descripcion}
                    </Typography>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Tipo de Ruta:
                        </Typography>
                        <Typography variant="body2">
                          {ROUTE_TYPES.find(t => t.value === route.tipo_ruta)?.label}
                        </Typography>
                      </Grid>

                      {route.distancia_km && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Distancia:
                          </Typography>
                          <Typography variant="body2">
                            {route.distancia_km.toFixed(2)} km
                          </Typography>
                        </Grid>
                      )}

                      {route.duracion_estimada && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Duración:
                          </Typography>
                          <Typography variant="body2">
                            {route.duracion_estimada} min
                          </Typography>
                        </Grid>
                      )}

                      {route.vehiculo && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Vehículo:
                          </Typography>
                          <Typography variant="body2">
                            <TruckIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                            {route.vehiculo.placa}
                          </Typography>
                        </Grid>
                      )}

                      {route.conductor && (
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Conductor:
                          </Typography>
                          <Typography variant="body2">
                            {route.conductor.display_name}
                          </Typography>
                        </Grid>
                      )}

                      {route.hora_inicio && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Inicio:
                          </Typography>
                          <Typography variant="body2">
                            {formatTime(route.hora_inicio)}
                          </Typography>
                        </Grid>
                      )}

                      {route.hora_fin && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Fin:
                          </Typography>
                          <Typography variant="body2">
                            {formatTime(route.hora_fin)}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>

                  <CardActions>
                    <TextField
                      select
                      size="small"
                      value={route.estado}
                      onChange={(e) => handleUpdateStatus(route.id, e.target.value)}
                      sx={{ flexGrow: 1 }}
                    >
                      {ROUTE_STATUS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </TextField>
                    <Button
                      size="small"
                      startIcon={<TimelineIcon />}
                      onClick={() => handleOptimizeRoute(route.id)}
                    >
                      Optimizar
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {routes.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                No hay rutas registradas
              </Typography>
            </Paper>
          )}
        </>
      )}

      {/* Dialog para crear ruta */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Ruta</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nombre de la Ruta"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Descripción"
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Tipo de Ruta"
                value={formData.tipo_ruta}
                onChange={(e) => setFormData({ ...formData, tipo_ruta: e.target.value })}
              >
                {ROUTE_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Zona"
                value={formData.zona_id}
                onChange={(e) => setFormData({ ...formData, zona_id: e.target.value })}
              >
                {zones.map((zone) => (
                  <MenuItem key={zone.id} value={zone.id}>
                    {zone.nombre}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpenDialog(false); resetForm(); }}>
            Cancelar
          </Button>
          <Button variant="contained" onClick={handleCreateRoute}>
            Crear Ruta
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RoutesPage;
