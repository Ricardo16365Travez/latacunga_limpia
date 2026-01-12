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
  IconButton,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Assignment as TaskIcon,
  CheckCircle as CheckIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
} from '@mui/icons-material';
import tareasService from '../../services/tareasService';
import { toErrorMessage } from '../../services/errorUtils';

interface Task {
  id: number;
  titulo: string;
  descripcion: string;
  estado?: string;
  prioridad?: string;
  tipo?: string;
  asignado_a?: {
    display_name: string;
    email: string;
  };
  ruta?: {
    nombre: string;
  };
  fecha_limite?: string;
  progreso?: number;
  created_at?: string;
  updated_at?: string;
}

const TASK_TYPES = [
  { value: 'RECOLECCION', label: 'Recolección' },
  { value: 'MANTENIMIENTO', label: 'Mantenimiento' },
  { value: 'LIMPIEZA', label: 'Limpieza' },
  { value: 'INSPECCION', label: 'Inspección' },
  { value: 'OTRO', label: 'Otro' },
];

const TASK_STATUS = [
  { value: 'PENDIENTE', label: 'Pendiente', color: '#757575' },
  { value: 'EN_PROGRESO', label: 'En Progreso', color: '#2196f3' },
  { value: 'COMPLETADA', label: 'Completada', color: '#4caf50' },
  { value: 'CANCELADA', label: 'Cancelada', color: '#f44336' },
];

const PRIORITY_LEVELS = [
  { value: 'BAJA', label: 'Baja', color: '#4caf50' },
  { value: 'MEDIA', label: 'Media', color: '#ff9800' },
  { value: 'ALTA', label: 'Alta', color: '#f44336' },
];

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    tipo: 'RECOLECCION',
    prioridad: 'MEDIA',
    fecha_limite: '',
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await tareasService.listarTareas();
      setTasks((data.tareas || []) as any);
    } catch (err: any) {
      setError(toErrorMessage(err) || 'Error al cargar tareas');
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    setError('Crear tareas no está disponible en el backend actual.');
  };

  const handleUpdateStatus = async (id: number, estado: string) => {
    setError('Actualizar tareas no está disponible en el backend actual.');
  };

  const handleStartTask = async (id: number) => {
    setError('Iniciar tareas no está disponible en el backend actual.');
  };

  const handleCompleteTask = async (id: number) => {
    setError('Completar tareas no está disponible en el backend actual.');
  };

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm('¿Está seguro de eliminar esta tarea?')) return;
    
    setError('Eliminar tareas no está disponible en el backend actual.');
  };

  const resetForm = () => {
    setFormData({
      titulo: '',
      descripcion: '',
      tipo: 'RECOLECCION',
      prioridad: 'MEDIA',
      fecha_limite: '',
    });
  };

  const getPriorityColor = (prioridad: string) => {
    return PRIORITY_LEVELS.find(p => p.value === prioridad)?.color || '#757575';
  };

  const getStatusColor = (estado: string) => {
    return TASK_STATUS.find(s => s.value === estado)?.color || '#757575';
  };

  const formatDate = (date?: string) => {
    if (!date) return 'Sin fecha límite';
    return new Date(date).toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const isOverdue = (task: Task) => {
    if (!task.fecha_limite || task.estado === 'COMPLETADA') return false;
    return new Date(task.fecha_limite) < new Date();
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <TaskIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Gestión de Tareas
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadTasks}
            sx={{ mr: 2 }}
          >
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Nueva Tarea
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
          {/* Estadísticas */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  Total Tareas
                </Typography>
                <Typography variant="h4">{tasks.length}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  Pendientes
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {tasks.filter(t => t.estado === 'PENDIENTE').length}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  En Progreso
                </Typography>
                <Typography variant="h4" color="info.main">
                  {tasks.filter(t => t.estado === 'EN_PROGRESO').length}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  Completadas
                </Typography>
                <Typography variant="h4" color="success.main">
                  {tasks.filter(t => t.estado === 'COMPLETADA').length}
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Lista de Tareas */}
          <Grid container spacing={3}>
            {tasks.map((task) => (
              <Grid item xs={12} md={6} lg={4} key={task.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Chip
                        label={TASK_TYPES.find(t => t.value === task.tipo)?.label}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={task.prioridad}
                        size="small"
                        sx={{
                          bgcolor: getPriorityColor(task.prioridad || 'MEDIA'),
                          color: 'white',
                        }}
                      />
                    </Box>

                    <Typography variant="h6" component="div" gutterBottom>
                      {task.titulo}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {task.descripcion}
                    </Typography>

                    {task.asignado_a && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        Asignado a: {task.asignado_a.display_name}
                      </Typography>
                    )}

                    {task.ruta && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        Ruta: {task.ruta.nombre}
                      </Typography>
                    )}

                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          Progreso
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {task.progreso}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={task.progreso}
                        sx={{ height: 8, borderRadius: 1 }}
                      />
                    </Box>

                    <Box sx={{ mt: 2 }}>
                      <Chip
                        label={TASK_STATUS.find(s => s.value === task.estado)?.label}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(task.estado || 'PENDIENTE'),
                          color: 'white',
                        }}
                      />
                      {isOverdue(task) && (
                        <Chip
                          label="Vencida"
                          size="small"
                          color="error"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Box>

                    <Typography
                      variant="caption"
                      display="block"
                      color={isOverdue(task) ? 'error' : 'text.secondary'}
                      sx={{ mt: 1 }}
                    >
                      Fecha límite: {formatDate(task.fecha_limite)}
                    </Typography>
                  </CardContent>

                  <CardActions>
                    {task.estado === 'PENDIENTE' && (
                      <Button
                        size="small"
                        startIcon={<StartIcon />}
                        onClick={() => handleStartTask(task.id)}
                      >
                        Iniciar
                      </Button>
                    )}
                    {task.estado === 'EN_PROGRESO' && (
                      <Button
                        size="small"
                        startIcon={<CheckIcon />}
                        color="success"
                        onClick={() => handleCompleteTask(task.id)}
                      >
                        Completar
                      </Button>
                    )}
                    <TextField
                      select
                      size="small"
                      value={task.estado}
                      onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
                      sx={{ flexGrow: 1, ml: 1 }}
                    >
                      {TASK_STATUS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </TextField>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteTask(task.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {tasks.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                No hay tareas registradas
              </Typography>
            </Paper>
          )}
        </>
      )}

      {/* Dialog para crear tarea */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Tarea</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Título"
                value={formData.titulo}
                onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
              />
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

            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Tipo de Tarea"
                value={formData.tipo}
                onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
              >
                {TASK_TYPES.map((type) => (
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
                label="Prioridad"
                value={formData.prioridad}
                onChange={(e) => setFormData({ ...formData, prioridad: e.target.value })}
              >
                {PRIORITY_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                type="date"
                label="Fecha Límite"
                value={formData.fecha_limite}
                onChange={(e) => setFormData({ ...formData, fecha_limite: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpenDialog(false); resetForm(); }}>
            Cancelar
          </Button>
          <Button variant="contained" onClick={handleCreateTask}>
            Crear Tarea
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TasksPage;
