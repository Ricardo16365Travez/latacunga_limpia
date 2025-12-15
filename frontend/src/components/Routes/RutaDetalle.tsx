import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Box,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  Grid,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import * as routesService from '../../services/routesService';
import { dibujarRutaRoja } from '../../services/routingMap';

// Fix para ícono de leaflet en React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface RutaDetalles {
  ruta: {
    id: number;
    zona: string;
    estado: string;
    suma_gravedad: number;
    camiones_usados: number;
    duracion_estimada: string;
    costo_total_metros: number;
    fecha_generacion: string;
  };
  incidencias: Array<{
    id: number;
    tipo: string;
    gravedad: number;
    lat: number;
    lon: number;
    descripcion: string;
    estado: string;
  }>;
  puntos: Array<{
    id: number;
    orden: number;
    camion_tipo: string;
    camion_id: string;
    tipo_punto: string;
    lat: number;
    lon: number;
    incidencia_id?: number;
  }>;
}

export default function RutaDetalle() {
  const { rutaId } = useParams<{ rutaId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RutaDetalles | null>(null);
  const mapRef = React.useRef<L.Map | null>(null);

  useEffect(() => {
    cargarDetalles();
  }, [rutaId]);

  const cargarDetalles = async () => {
    if (!rutaId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await routesService.obtenerDetallesRuta(Number(rutaId));
      setData(response);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error al cargar detalles de ruta');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (data && mapRef.current && data.puntos.length > 0) {
      const puntos = data.puntos.map(p => ({ lat: p.lat, lon: p.lon }));
      dibujarRutaRoja(mapRef.current, puntos);
    }
  }, [data]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !data) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/rutas')}
          sx={{ mb: 2 }}
        >
          Volver
        </Button>
        <Alert severity="error">{error || 'No se encontraron datos de la ruta'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/rutas')}
        >
          Volver
        </Button>
        <Typography variant="h4">🗺️ Ruta #{data.ruta.id} - {data.ruta.zona}</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={cargarDetalles}
        >
          Recargar
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Mapa */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '500px' }}>
            <MapContainer
              ref={mapRef}
              center={[-0.936, -78.613]}
              zoom={13}
              style={{ height: '100%', borderRadius: '4px' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
              />
              {/* Marcadores de puntos */}
              {data.puntos.map((punto, idx) => (
                <Marker key={punto.id} position={[punto.lat, punto.lon]}>
                  <Popup>
                    <Box>
                      <Typography variant="body2">
                        <strong>Punto {punto.orden}</strong>
                      </Typography>
                      <Typography variant="caption">
                        Tipo: {punto.tipo_punto}
                      </Typography>
                      <br />
                      <Typography variant="caption">
                        Camión: {punto.camion_id}
                      </Typography>
                      {punto.incidencia_id && (
                        <>
                          <br />
                          <Typography variant="caption">
                            Incidencia: #{punto.incidencia_id}
                          </Typography>
                        </>
                      )}
                    </Box>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </Paper>
        </Grid>

        {/* Panel de información */}
        <Grid item xs={12} md={4}>
          {/* Info de ruta */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                📋 Información de Ruta
              </Typography>
              <Divider sx={{ mb: 1 }} />
              <Typography variant="body2"><strong>Zona:</strong> {data.ruta.zona}</Typography>
              <Typography variant="body2"><strong>Estado:</strong> {data.ruta.estado}</Typography>
              <Typography variant="body2"><strong>Gravedad Total:</strong> {data.ruta.suma_gravedad} pts</Typography>
              <Typography variant="body2"><strong>Camiones:</strong> {data.ruta.camiones_usados}</Typography>
              <Typography variant="body2"><strong>Duración:</strong> {data.ruta.duracion_estimada}</Typography>
              <Typography variant="body2"><strong>Distancia:</strong> {(data.ruta.costo_total_metros / 1000).toFixed(2)} km</Typography>
              <Typography variant="caption" color="textSecondary">
                Generada: {new Date(data.ruta.fecha_generacion).toLocaleString('es-ES')}
              </Typography>
            </CardContent>
          </Card>

          {/* Lista de incidencias */}
          {data.incidencias && data.incidencias.length > 0 && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  🔴 Incidencias ({data.incidencias.length})
                </Typography>
                <Divider sx={{ mb: 1 }} />
                <List dense>
                  {data.incidencias.map((inc) => (
                    <ListItem key={inc.id} disablePadding sx={{ mb: 1 }}>
                      <ListItemText
                        primary={`#${inc.id} - ${inc.tipo}`}
                        secondary={`Gravedad: ${inc.gravedad} | ${inc.descripcion?.substring(0, 30)}...`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Lista de puntos */}
          {data.puntos && data.puntos.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  📍 Puntos ({data.puntos.length})
                </Typography>
                <Divider sx={{ mb: 1 }} />
                <List dense>
                  {data.puntos.map((punto) => (
                    <ListItem key={punto.id} disablePadding sx={{ mb: 1 }}>
                      <ListItemText
                        primary={`Punto ${punto.orden}`}
                        secondary={`${punto.tipo_punto} | ${punto.camion_id}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}
