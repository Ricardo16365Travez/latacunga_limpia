import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Box,
  Alert,
  CircularProgress,
  MenuItem,
  TextField,
} from '@mui/material';
import {
  Assessment as ReportIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  BarChart as ChartIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import reportesService from '../services/reportesService';

interface Stats {
  total_incidencias: number;
  incidencias_por_estado: Record<string, number>;
  incidencias_por_tipo: Record<string, number>;
  total_rutas: number;
  rutas_activas: number;
  total_tareas: number;
  tareas_completadas: number;
  tareas_pendientes: number;
}

const COLORS = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0', '#00bcd4'];

const ReportesPage: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });


  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportesService.reporteEstadisticas({
        fecha_inicio: dateRange.start,
        fecha_fin: dateRange.end,
      });
      // Adaptar estructura a la UI esperada
      setStats({
        total_incidencias: data.total_incidencias || 0,
        incidencias_por_estado: (data as any).incidencias_por_estado || {},
        incidencias_por_tipo: data.incidencias_por_tipo || {},
        total_rutas: data.total_rutas || 0,
        rutas_activas: 0,
        total_tareas: 0,
        tareas_completadas: 0,
        tareas_pendientes: 0,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar estadísticas');
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  }, [dateRange.start, dateRange.end]);

  useEffect(() => {
    loadStats();
  }, [dateRange, loadStats]);

  const handleExportPDF = async () => {
    try {
      if (!stats) {
        setError('No hay datos para exportar.');
        return;
      }

      const win = window.open('', 'PRINT', 'height=800,width=1000');
      if (!win) {
        setError('No se pudo abrir la ventana de impresión.');
        return;
      }

      const fecha = new Date().toLocaleString('es-EC');
      const estadoRows = Object.entries(stats.incidencias_por_estado)
        .map(([estado, cantidad]) => `<tr><td>${estado}</td><td>${cantidad}</td></tr>`) 
        .join('');
      const tipoRows = Object.entries(stats.incidencias_por_tipo)
        .map(([tipo, cantidad]) => `<tr><td>${tipo}</td><td>${cantidad}</td></tr>`) 
        .join('');

      const html = `
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <meta charset="utf-8" />
          <title>Reporte PDF</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; }
            h1 { margin: 0 0 8px; }
            h2 { margin-top: 24px; }
            .header { display:flex; justify-content:space-between; align-items:center; }
            .card { border:1px solid #ddd; border-radius:8px; padding:12px; margin:8px 0; }
            .grid { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:12px; }
            table { width:100%; border-collapse:collapse; margin-top:8px; }
            th, td { border:1px solid #ddd; padding:6px 8px; text-align:left; }
            th { background:#f5f5f5; }
            .meta { color:#555; font-size:12px; }
          </style>
        </head>
        <body>
          <div class="header">
            <div>
              <h1>Reporte y Estadísticas</h1>
              <div class="meta">Rango: ${dateRange.start} a ${dateRange.end}</div>
              <div class="meta">Generado: ${fecha}</div>
            </div>
          </div>
          <div class="card">
            <h2>Resumen</h2>
            <div class="grid">
              <div class="card"><strong>Incidencias</strong><div>${stats.total_incidencias}</div></div>
              <div class="card"><strong>Rutas</strong><div>${stats.total_rutas}</div></div>
              <div class="card"><strong>Tareas</strong><div>${stats.total_tareas}</div></div>
              <div class="card"><strong>Completadas</strong><div>${stats.tareas_completadas}</div></div>
            </div>
          </div>
          <div class="card">
            <h2>Incidencias por Estado</h2>
            <table>
              <thead><tr><th>Estado</th><th>Cantidad</th></tr></thead>
              <tbody>${estadoRows || '<tr><td colspan="2">Sin datos</td></tr>'}</tbody>
            </table>
          </div>
          <div class="card">
            <h2>Incidencias por Tipo</h2>
            <table>
              <thead><tr><th>Tipo</th><th>Cantidad</th></tr></thead>
              <tbody>${tipoRows || '<tr><td colspan="2">Sin datos</td></tr>'}</tbody>
            </table>
          </div>
        </body>
        </html>
      `;

      win.document.write(html);
      win.document.close();
      win.focus();
      // Esperar un pequeño tiempo para que el DOM se renderice antes de imprimir
      setTimeout(() => {
        win.print();
        win.close();
      }, 300);
    } catch (e) {
      console.error(e);
      setError('No se pudo generar el PDF.');
    }
  };

  const handleExportExcel = async () => {
    setError('Exportar Excel no está disponible en el backend actual.');
  };

  const incidentsByState = stats ? Object.entries(stats.incidencias_por_estado).map(([name, value]) => ({
    name,
    value,
  })) : [];

  const incidentsByType = stats ? Object.entries(stats.incidencias_por_tipo).map(([name, value]) => ({
    name,
    value,
  })) : [];

  const taskCompletion = stats ? [
    { name: 'Completadas', value: stats.tareas_completadas },
    { name: 'Pendientes', value: stats.tareas_pendientes },
  ] : [];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Reportes y Estadísticas
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadStats}
            sx={{ mr: 2 }}
          >
            Actualizar
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExportExcel}
            sx={{ mr: 1 }}
          >
            Excel
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExportPDF}
          >
            PDF
          </Button>
        </Box>
      </Box>

      {/* Filtros de Fecha */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Inicio"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Fin"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="contained"
              onClick={loadStats}
              startIcon={<ChartIcon />}
            >
              Generar Reporte
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : stats ? (
        <>
          {/* Tarjetas de Resumen */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Incidencias
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {stats.total_incidencias}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Rutas
                  </Typography>
                  <Typography variant="h3" color="info.main">
                    {stats.total_rutas}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stats.rutas_activas} activas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Tareas
                  </Typography>
                  <Typography variant="h3" color="warning.main">
                    {stats.total_tareas}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stats.tareas_completadas} completadas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Tasa de Completado
                  </Typography>
                  <Typography variant="h3" color="success.main">
                    {stats.total_tareas > 0
                      ? Math.round((stats.tareas_completadas / stats.total_tareas) * 100)
                      : 0}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Gráficos */}
          <Grid container spacing={3}>
            {/* Incidencias por Estado */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Incidencias por Estado
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={incidentsByState}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#2196f3" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            {/* Incidencias por Tipo */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Incidencias por Tipo
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={incidentsByType}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {incidentsByType.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            {/* Tareas - Completadas vs Pendientes */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Estado de Tareas
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={taskCompletion}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      <Cell fill="#4caf50" />
                      <Cell fill="#ff9800" />
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            {/* Gráfico de Resumen */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Resumen General
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={[
                      { name: 'Incidencias', value: stats.total_incidencias },
                      { name: 'Rutas', value: stats.total_rutas },
                      { name: 'Tareas', value: stats.total_tareas },
                      { name: 'Completadas', value: stats.tareas_completadas },
                    ]}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#4caf50" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>
        </>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No hay datos disponibles para el período seleccionado
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default ReportesPage;
