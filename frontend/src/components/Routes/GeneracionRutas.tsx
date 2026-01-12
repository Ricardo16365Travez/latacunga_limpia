import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
  Divider,
} from '@mui/material';
import { Add, CheckCircle, Warning, Info } from '@mui/icons-material';
import incidenciasService from '../../services/incidenciasService';

export default function GeneracionRutas() {
  const [loading, setLoading] = useState(false);
  const [zona, setZona] = useState<'oriental' | 'occidental'>('oriental');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [umbralInfo, setUmbralInfo] = useState<any | null>(null);
  const [rutaGenerada, _setRutaGenerada] = useState<any | null>(null);

  const verificarUmbral = useCallback(async () => {
    try {
      const data = await incidenciasService.verificarUmbralZona(zona);
      setUmbralInfo(data);
    } catch (err) {
      console.error('Error verificando umbral:', err);
    }
  }, [zona]);

  useEffect(() => {
    verificarUmbral();
  }, [verificarUmbral, zona]);

  const handleGenerarRuta = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      // En el backend Go, las rutas se generan automáticamente
      // cuando los incidentes en una zona alcanzan el umbral
      setSuccess(`En el backend Go, las rutas se generan automáticamente cuando hay incidentes acumulados en la zona ${zona}.`);
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || 'Error al generar ruta';
      setError(errorMsg);
      console.error('Error generando ruta:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Generación de Rutas Optimizadas
      </Typography>

      <Grid container spacing={3}>
        {/* Panel de Configuración */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuración
              </Typography>
              
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Zona</InputLabel>
                <Select
                  value={zona}
                  label="Zona"
                  onChange={(e) => setZona(e.target.value as 'oriental' | 'occidental')}
                >
                  <MenuItem value="oriental">Oriental</MenuItem>
                  <MenuItem value="occidental">Occidental</MenuItem>
                </Select>
              </FormControl>

              {/* Info del Umbral */}
              {umbralInfo && (
                <Paper elevation={0} sx={{ mt: 3, p: 2, bgcolor: umbralInfo.debe_generar_ruta ? '#fff3e0' : '#e3f2fd' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Estado del Umbral
                  </Typography>
                  <Typography variant="body2">
                    <strong>Suma de Gravedad:</strong> {umbralInfo.suma_gravedad || 0}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Umbral Configurado:</strong> {umbralInfo.umbral_configurado}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Incidencias Pendientes:</strong> {umbralInfo.incidencias_pendientes || 0}
                  </Typography>
                  
                  {umbralInfo.debe_generar_ruta ? (
                    <Chip
                      icon={<Warning />}
                      label="¡Umbral alcanzado! Se recomienda generar ruta"
                      color="warning"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  ) : (
                    <Chip
                      icon={<Info />}
                      label="Umbral no alcanzado"
                      color="info"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  )}
                </Paper>
              )}

              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleGenerarRuta}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <Add />}
                sx={{ mt: 3 }}
              >
                {loading ? 'Generando...' : 'Generar Ruta'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Panel de Resultados */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resultado
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
                  {success}
                </Alert>
              )}

              {rutaGenerada && (
                <Box>
                  <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          ID Ruta
                        </Typography>
                        <Typography variant="h6">
                          #{rutaGenerada.id}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Zona
                        </Typography>
                        <Typography variant="h6">
                          {rutaGenerada.zona}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Estado
                        </Typography>
                        <Chip label={rutaGenerada.estado} color="success" size="small" />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Camiones Necesarios
                        </Typography>
                        <Typography variant="h6">
                          {rutaGenerada.camiones_usados}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Suma Gravedad
                        </Typography>
                        <Typography variant="h6">
                          {rutaGenerada.suma_gravedad} puntos
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Duración Estimada
                        </Typography>
                        <Typography variant="h6">
                          {rutaGenerada.duracion_estimada}
                        </Typography>
                      </Grid>
                      {rutaGenerada.costo_total_metros && (
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            Distancia Total
                          </Typography>
                          <Typography variant="h6">
                            {(rutaGenerada.costo_total_metros / 1000).toFixed(2)} km
                          </Typography>
                        </Grid>
                      )}
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="textSecondary">
                          Fecha Generación
                        </Typography>
                        <Typography variant="body1">
                          {new Date(rutaGenerada.fecha_generacion).toLocaleString('es-EC')}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Próximos Pasos:
                  </Typography>
                  <Typography variant="body2">
                    1. La ruta ha sido generada y está en estado <strong>planeada</strong>
                  </Typography>
                  <Typography variant="body2">
                    2. Asigna conductores desde el panel de administración
                  </Typography>
                  <Typography variant="body2">
                    3. Los conductores podrán iniciar la ruta desde "Mis Rutas"
                  </Typography>
                </Box>
              )}

              {!rutaGenerada && !error && !loading && (
                <Box textAlign="center" py={4}>
                  <Typography variant="body1" color="textSecondary">
                    Selecciona una zona y haz clic en "Generar Ruta" para crear una ruta optimizada
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
