import React from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
} from '@mui/material';
import IncidentsPage from '../Incidents/IncidentsPage';
import RoutesPage from '../Routes/RoutesPage';
import TasksPage from '../Tasks/TasksPage';
import NotificationsPage from '../Notifications/NotificationsPage';
import ReportsPage from '../Reports/ReportsPage';

interface DashboardProps {
  userRole: string;
}

const HomePage: React.FC<{ userRole: string }> = ({ userRole }) => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="h1" gutterBottom color="primary">
                ¡Bienvenido al Sistema de Gestión de Residuos!
              </Typography>
              <Typography variant="body1" paragraph>
                Plataforma web modular diseñada para centralizar reportes ciudadanos, 
                optimizar rutas de recolección y gestionar de manera eficiente los residuos 
                en la ciudad de Latacunga.
              </Typography>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                🎯 Funcionalidades Principales:
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ p: 2, cursor: 'pointer' }} onClick={() => navigate('/incidents')}>
                    <Typography variant="h6" color="primary" gutterBottom>
                      📊 Reportes Ciudadanos
                    </Typography>
                    <Typography variant="body2">
                      Los ciudadanos pueden reportar problemas de residuos con ubicación 
                      geoespacial, fotos y descripción detallada.
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ p: 2, cursor: 'pointer' }} onClick={() => navigate('/routes')}>
                    <Typography variant="h6" color="primary" gutterBottom>
                      🗺️ Gestión de Rutas
                    </Typography>
                    <Typography variant="body2">
                      Optimización de rutas de recolección con mapas interactivos 
                      y planificación eficiente de recursos.
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ p: 2, cursor: 'pointer' }} onClick={() => navigate('/tasks')}>
                    <Typography variant="h6" color="primary" gutterBottom>
                      ✅ Gestión de Tareas
                    </Typography>
                    <Typography variant="body2">
                      Asignación y seguimiento de tareas para el personal operativo 
                      con sistema de estados y prioridades.
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ p: 2, cursor: 'pointer' }} onClick={() => navigate('/reports')}>
                    <Typography variant="h6" color="primary" gutterBottom>
                      📈 Reportes y Estadísticas
                    </Typography>
                    <Typography variant="body2">
                      Generación de reportes detallados y visualización de estadísticas 
                      para la toma de decisiones estratégicas.
                    </Typography>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom color="secondary">
                🔧 Panel de Control - {userRole}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    onClick={() => navigate('/incidents')}
                  >
                    📝 Incidencias
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    onClick={() => navigate('/routes')}
                  >
                    🗺️ Rutas
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    onClick={() => navigate('/tasks')}
                  >
                    ✅ Tareas
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    onClick={() => navigate('/reports')}
                  >
                    📊 Estadísticas
                  </Button>
                </Grid>
              </Grid>
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  onClick={() => navigate('/notifications')}
                >
                  🔔 Notificaciones
                </Button>
              </Box>
              <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
                Sistema con autenticación JWT integrada y gestión de roles.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              🏗️ Estado del Sistema
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Backend</Typography>
                    <Typography variant="body2">✅ Django + PostgreSQL</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Frontend</Typography>
                    <Typography variant="body2">✅ React + TypeScript</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">RabbitMQ</Typography>
                    <Typography variant="body2">✅ Messaging System</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Redis</Typography>
                    <Typography variant="body2">✅ Cache y Cola</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

const Dashboard: React.FC<DashboardProps> = ({ userRole }) => {
  return (
    <Routes>
      <Route path="/" element={<HomePage userRole={userRole} />} />
      <Route path="/incidents" element={<IncidentsPage />} />
      <Route path="/routes" element={<RoutesPage />} />
      <Route path="/tasks" element={<TasksPage />} />
      <Route path="/notifications" element={<NotificationsPage />} />
      <Route path="/reports" element={<ReportsPage />} />
    </Routes>
  );
};

export default Dashboard;