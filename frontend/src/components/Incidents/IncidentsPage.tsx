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
  IconButton,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  LocationOn as LocationIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  PictureAsPdf as PdfIcon,
} from '@mui/icons-material';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import IncidenciasService from '../../services/incidenciasService';
import { toErrorMessage } from '../../services/errorUtils';

// Fix para íconos de Leaflet en React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface Incident {
  id: number;
  tipo: string;
  descripcion: string;
  gravedad: number;
  estado: string;
  lat?: number;
  lon?: number;
  zona: string;
  usuario_id?: number;
  reportado_en?: string;
  created_at?: string;
  direccion?: string; // Dirección obtenida por geocodificación reversa
}

const INCIDENT_TYPES = [
  { value: 'acopio', label: 'Punto de Acopio' },
  { value: 'zona_critica', label: 'Zona Crítica' },
  { value: 'animal_muerto', label: 'Animal Muerto' },
];

const GRAVEDAD_LEVELS = [
  { value: 1, label: 'Baja', color: '#4caf50' },
  { value: 3, label: 'Media', color: '#ff9800' },
  { value: 5, label: 'Alta', color: '#f44336' },
];

const STATUS_OPTIONS = [
  { value: 'pendiente', label: 'Pendiente', color: '#757575' },
  { value: 'validada', label: 'Validada', color: '#9c27b0' },
  { value: 'asignada', label: 'Asignada', color: '#2196f3' },
  { value: 'completada', label: 'Completada', color: '#4caf50' },
  { value: 'cancelada', label: 'Cancelada', color: '#f44336' },
];

const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    tipo: 'acopio',
    descripcion: '',
    gravedad: 3,
    zona: 'occidental',
    latitud: -0.9346,
    longitud: -78.6156,
  });

  useEffect(() => {
    loadIncidents();
  }, []);

  // Geocodificación reversa para obtener dirección desde coordenadas
  const fetchAddress = async (lat: number, lon: number): Promise<string> => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&addressdetails=1`
      );
      const data = await response.json();
      if (data.address) {
        const { road, house_number, neighbourhood, suburb, city, town, village } = data.address;
        const parts = [
          house_number,
          road,
          neighbourhood || suburb,
          city || town || village
        ].filter(Boolean);
        return parts.join(', ') || 'Dirección no disponible';
      }
      return 'Dirección no disponible';
    } catch (error) {
      console.error('Error obteniendo dirección:', error);
      return 'Dirección no disponible';
    }
  };

  const loadIncidents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await IncidenciasService.listarIncidencias();
      // El backend devuelve un array directo: List[IncidenciaResponse]
      const incidentsList = Array.isArray(data) ? data : (data?.incidents || data?.results || []);
      
      // Obtener direcciones para cada incidencia con coordenadas
      const incidentsWithAddress = await Promise.all(
        incidentsList.map(async (incident: Incident) => {
          if (incident.lat && incident.lon && !incident.direccion) {
            const direccion = await fetchAddress(incident.lat, incident.lon);
            return { ...incident, direccion };
          }
          return incident;
        })
      );
      
      setIncidents(incidentsWithAddress);
    } catch (err: any) {
      setError(toErrorMessage(err) || 'Error al cargar incidencias');
      console.error('Error loading incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIncident = async () => {
    try {
      const lat = typeof formData.latitud === 'number' && !isNaN(formData.latitud) ? formData.latitud : null;
      const lon = typeof formData.longitud === 'number' && !isNaN(formData.longitud) ? formData.longitud : null;
      
      const payload = {
        tipo: formData.tipo,
        descripcion: formData.descripcion.trim(),
        gravedad: Number(formData.gravedad) || 2,
        lat,
        lon,
        zona: formData.zona.trim(),
        foto_url: null,
        usuario_id: 1,
      };
      
      console.log('[DEBUG] Payload enviado:', payload);
      await IncidenciasService.crearIncidencia(payload);
      setOpenDialog(false);
      resetForm();
      loadIncidents();
    } catch (err: any) {
      const errorMsg = toErrorMessage(err) || 'Error al crear incidencia';
      console.error('[ERROR] Crear incidencia:', err, errorMsg);
      setError(errorMsg);
    }
  };

  const handleUpdateStatus = async (id: number, estado: string) => {
    try {
      await IncidenciasService.actualizarIncidencia(id, { estado });
      loadIncidents();
    } catch (err: any) {
      setError(toErrorMessage(err) || 'Error al actualizar estado');
    }
  };

  const handleDeleteIncident = async (id: number) => {
    if (!window.confirm('¿Está seguro de eliminar esta incidencia?')) return;
    
    try {
      await IncidenciasService.eliminarIncidencia(id);
      loadIncidents();
    } catch (err: any) {
      setError(toErrorMessage(err) || 'Error al eliminar incidencia');
    }
  };

  const handleGeneratePDF = (incident: Incident) => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      setError('No se pudo abrir la ventana de impresión. Verifica los permisos del navegador.');
      return;
    }

    const tipoLabel = INCIDENT_TYPES.find(t => t.value === incident.tipo)?.label || incident.tipo;
    const estadoLabel = STATUS_OPTIONS.find(s => s.value === incident.estado)?.label || incident.estado;
    const gravedadLabel = GRAVEDAD_LEVELS.find(g => g.value === incident.gravedad)?.label || `Nivel ${incident.gravedad}`;

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Reporte de Incidencia #${incident.id}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 40px;
            color: #333;
          }
          .header {
            text-align: center;
            border-bottom: 3px solid #2196f3;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          .logo {
            font-size: 24px;
            font-weight: bold;
            color: #2196f3;
          }
          .title {
            font-size: 20px;
            margin-top: 10px;
          }
          .section {
            margin-bottom: 20px;
          }
          .label {
            font-weight: bold;
            color: #666;
            display: inline-block;
            width: 150px;
          }
          .value {
            color: #333;
          }
          .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            background-color: #e0e0e0;
            font-size: 14px;
            margin-left: 10px;
          }
          .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 12px;
            color: #666;
          }
          @media print {
            body { padding: 20px; }
            .no-print { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="logo">EPAGAL - Latacunga</div>
          <div class="title">Reporte de Incidencia #${incident.id}</div>
        </div>

        <div class="section">
          <div><span class="label">Tipo:</span> <span class="value">${tipoLabel}</span></div>
        </div>

        <div class="section">
          <div><span class="label">Descripción:</span></div>
          <div class="value" style="margin-top: 10px;">${incident.descripcion || 'Sin descripción'}</div>
        </div>

        <div class="section">
          <div><span class="label">Gravedad:</span> <span class="value">${gravedadLabel}</span></div>
        </div>

        <div class="section">
          <div><span class="label">Estado:</span> <span class="value">${estadoLabel}</span></div>
        </div>

        <div class="section">
          <div><span class="label">Zona:</span> <span class="value">${incident.zona || 'No especificada'}</span></div>
        </div>

        <div class="section">
          <div><span class="label">Dirección:</span></div>
          <div class="value" style="margin-top: 5px;">${incident.direccion || 'No disponible'}</div>
        </div>

        <div class="section">
          <div><span class="label">Coordenadas:</span> <span class="value">Lat: ${incident.lat?.toFixed(6) || 'N/A'}, Lon: ${incident.lon?.toFixed(6) || 'N/A'}</span></div>
        </div>

        <div class="section">
          <div><span class="label">Fecha de Reporte:</span> <span class="value">${incident.created_at ? new Date(incident.created_at).toLocaleString('es-EC') : 'No disponible'}</span></div>
        </div>

        <div class="footer">
          <p>Sistema de Gestión de Incidencias - EPAGAL Latacunga</p>
          <p>Generado: ${new Date().toLocaleString('es-EC')}</p>
        </div>

        <div class="no-print" style="text-align: center; margin-top: 30px;">
          <button onclick="window.print()" style="padding: 10px 30px; background-color: #2196f3; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">Imprimir / Guardar PDF</button>
        </div>
      </body>
      </html>
    `;

    printWindow.document.write(html);
    printWindow.document.close();
  };

  const resetForm = () => {
    setFormData({
      tipo: 'ACUMULACION',
      descripcion: '',
      gravedad: 2,
      zona: 'Latacunga',
      latitud: -0.9346,
      longitud: -78.6156,
    });
  };

  const getGravedadColor = (gravedad: number) => {
    return GRAVEDAD_LEVELS.find(p => p.value === gravedad)?.color || '#757575';
  };

  const getStatusColor = (estado: string) => {
    return STATUS_OPTIONS.find(s => s.value === estado)?.color || '#757575';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Gestión de Incidencias
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadIncidents}
            sx={{ mr: 2 }}
          >
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Nueva Incidencia
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
          {/* Mapa */}
          <Paper sx={{ p: 2, mb: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Mapa de Incidencias
            </Typography>
            <MapContainer
              center={[-0.9346, -78.6156]}
              zoom={13}
              maxBounds={[
                [-1.05, -78.75],  // Esquina suroeste (límite sur y oeste)
                [-0.82, -78.48]   // Esquina noreste (límite norte y este)
              ]}
              maxBoundsViscosity={1.0}
              minZoom={12}
              maxZoom={18}
              style={{ height: '350px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              />
              {incidents
                .map((incident) => {
                  const lat = incident.lat;
                  const lon = incident.lon;
                  if (lat === undefined || lon === undefined) return null;
                  return (
                    <Marker
                      key={incident.id}
                      position={[lat, lon]}
                    >
                      <Popup>
                        <strong>{INCIDENT_TYPES.find(t => t.value === incident.tipo)?.label || incident.tipo}</strong>
                        <br />
                        {incident.descripcion}
                        <br />
                        <Box sx={{ mt: 1, mb: 1 }}>
                          <LocationIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5, fontSize: 14 }} />
                          <Typography variant="caption" component="span">
                            {incident.direccion || 'Obteniendo dirección...'}
                          </Typography>
                        </Box>
                        <Chip
                          label={`Gravedad ${incident.gravedad ?? 1}`}
                          size="small"
                          sx={{
                            mt: 1,
                            bgcolor: getGravedadColor(incident.gravedad ?? 1),
                            color: 'white',
                          }}
                        />
                      </Popup>
                    </Marker>
                  );
                })
                .filter(Boolean)}
            </MapContainer>
          </Paper>

          {/* Lista de Incidencias */}
          <Grid container spacing={3}>
            {incidents.map((incident) => (
              <Grid item xs={12} sm={6} md={4} key={incident.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Chip
                        label={INCIDENT_TYPES.find(t => t.value === incident.tipo)?.label}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={`Gravedad ${incident.gravedad}`}
                        size="small"
                        sx={{
                          bgcolor: getGravedadColor(incident.gravedad),
                          color: 'white',
                        }}
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {incident.descripcion}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <LocationIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                      <Typography variant="caption" color="text.secondary">
                        Zona: {incident.zona}
                      </Typography>
                    </Box>

                    <Chip
                      label={STATUS_OPTIONS.find(s => s.value === incident.estado)?.label || 'Reportada'}
                      size="small"
                      sx={{
                        bgcolor: getStatusColor(incident.estado || 'REPORTADA'),
                        color: 'white',
                      }}
                    />

                    <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                      Creado: {incident.created_at ? new Date(incident.created_at).toLocaleDateString() : 'N/D'}
                    </Typography>
                  </CardContent>
                  
                  <CardActions>
                    <TextField
                      select
                      size="small"
                      value={incident.estado}
                      onChange={(e) => handleUpdateStatus(incident.id, e.target.value)}
                      sx={{ flexGrow: 1 }}
                    >
                      {STATUS_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </TextField>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleGeneratePDF(incident)}
                      title="Generar PDF"
                    >
                      <PdfIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteIncident(incident.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {incidents.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                No hay incidencias registradas
              </Typography>
            </Paper>
          )}
        </>
      )}

      {/* Dialog para crear incidencia */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Incidencia</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Tipo de Incidencia"
                value={formData.tipo}
                onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
              >
                {INCIDENT_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Descripción"
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Gravedad"
                value={formData.gravedad}
                onChange={(e) => setFormData({ ...formData, gravedad: Number(e.target.value) })}
              >
                {GRAVEDAD_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Zona"
                value={formData.zona}
                onChange={(e) => setFormData({ ...formData, zona: e.target.value })}
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                type="number"
                label="Latitud"
                value={formData.latitud}
                onChange={(e) => setFormData({ ...formData, latitud: parseFloat(e.target.value) })}
                inputProps={{ step: 0.0001 }}
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                type="number"
                label="Longitud"
                value={formData.longitud}
                onChange={(e) => setFormData({ ...formData, longitud: parseFloat(e.target.value) })}
                inputProps={{ step: 0.0001 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpenDialog(false); resetForm(); }}>
            Cancelar
          </Button>
          <Button variant="contained" onClick={handleCreateIncident}>
            Crear Incidencia
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default IncidentsPage;
