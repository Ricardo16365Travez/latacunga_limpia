import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Box,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Map as MapIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import rutasService from '../../services/rutasService';

interface Ruta {
  id: number;
  zona: string;
  estado: string;
  suma_gravedad: number;
  camiones_usados: number;
  duracion_estimada?: string;
  asignaciones?: any[];
  fecha_generacion?: string;
}

export default function MisRutas() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rutas, setRutas] = useState<Ruta[]>([]);
  const [notasRuta, setNotasRuta] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [finalizandoRutaId, setFinalizandoRutaId] = useState<number | null>(null);

  useEffect(() => {
    cargarRutas();
  }, []);

  const cargarRutas = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await rutasService.listarRutas({ limit: 100 });
      const rutasList = Array.isArray(response) ? response : (response?.results || []);
      setRutas(rutasList);
    } catch (err: any) {
      console.error('Error cargando rutas:', err);
      setRutas([]);
      setError('Error al cargar rutas. Verifica la conexión con el backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleIniciarRuta = async (rutaId: number) => {
    try {
      await rutasService.actualizarRuta(rutaId, { estado: 'en_ejecucion' });
      await cargarRutas();
    } catch (err) {
      setError('Error al iniciar la ruta');
    }
  };

  const handleFinalizarRuta = (rutaId: number) => {
    setFinalizandoRutaId(rutaId);
    setDialogOpen(true);
  };

  const confirmarFinalizarRuta = async () => {
    if (finalizandoRutaId) {
      try {
        await rutasService.actualizarRuta(finalizandoRutaId, { estado: 'completada' });
        await cargarRutas();
      } catch (err) {
        setError('Error al finalizar la ruta');
      }
    }
    setDialogOpen(false);
    setNotasRuta('');
    setFinalizandoRutaId(null);
  };

  const handleVerMapa = (rutaId: number) => {
    navigate(`/rutas/${rutaId}`);
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'planeada':
        return 'info';
      case 'en_ejecucion':
        return 'warning';
      case 'completada':
        return 'success';
      case 'asignada':
        return 'primary';
      default:
        return 'default';
    }
  };

  const stats = {
    total: rutas.length,
    asignado: rutas.filter((r) => r.estado === 'asignada').length,
    iniciado: rutas.filter((r) => r.estado === 'en_ejecucion').length,
    completado: rutas.filter((r) => r.estado === 'completada').length,
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">📍 Mis Rutas Asignadas</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={cargarRutas}
        >
          Recargar
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Resumen de estados */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">{stats.asignado}</Typography>
            <Typography variant="body2" color="textSecondary">Asignadas</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#fff3e0' }}>
            <Typography variant="h6">{stats.iniciado}</Typography>
            <Typography variant="body2" color="textSecondary">En progreso</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e8f5e9' }}>
            <Typography variant="h6">{stats.completado}</Typography>
            <Typography variant="body2" color="textSecondary">Completadas</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">{stats.total}</Typography>
            <Typography variant="body2" color="textSecondary">Total</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Lista de rutas */}
      {rutas.length > 0 ? (
        <Grid container spacing={2}>
          {rutas.map((ruta) => (
            <Grid item xs={12} sm={6} md={4} key={ruta.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                    <Typography variant="h6">Ruta #{ruta.id}</Typography>
                    <Chip
                      label={ruta.estado}
                      color={ruta.estado === 'iniciado' ? 'warning' : ruta.estado === 'completado' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Zona:</strong> {ruta.zona}
                  </Typography>

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Gravedad:</strong> {ruta.suma_gravedad} pts
                  </Typography>

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Camiones:</strong> {ruta.camiones_usados}
                  </Typography>

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Duración:</strong> {ruta.duracion_estimada}
                  </Typography>

                  {ruta.asignaciones && ruta.asignaciones.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                        Asignaciones:
                      </Typography>
                      <List dense>
                        {ruta.asignaciones.map((asig, idx) => (
                          <ListItem key={idx} dense>
                            <ListItemText
                              primary={asig.camion_id}
                              secondary={`Tipo: ${asig.camion_tipo} | Estado: ${asig.estado}`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    startIcon={<MapIcon />}
                    onClick={() => handleVerMapa(ruta.id)}
                  >
                    Mapa
                  </Button>

                  {ruta.estado === 'asignado' && (
                    <Button
                      variant="contained"
                      color="success"
                      size="small"
                      startIcon={<PlayIcon />}
                      onClick={() => handleIniciarRuta(ruta.id)}
                    >
                      Iniciar
                    </Button>
                  )}

                  {ruta.estado === 'iniciado' && (
                    <Button
                      variant="contained"
                      color="error"
                      size="small"
                      startIcon={<StopIcon />}
                      onClick={() => handleFinalizarRuta(ruta.id)}
                    >
                      Finalizar
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No tienes rutas asignadas actualmente.
          </Typography>
        </Paper>
      )}

      {/* Diálogo para finalizar ruta */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Finalizar Ruta</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            ¿Estás seguro de que deseas finalizar esta ruta? Puedes agregar notas sobre su ejecución.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Notas sobre la ruta (opcional)..."
            value={notasRuta}
            onChange={(e) => setNotasRuta(e.target.value)}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
          <Button onClick={confirmarFinalizarRuta} variant="contained" color="primary">
            Finalizar Ruta
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
