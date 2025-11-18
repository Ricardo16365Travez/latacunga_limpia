import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
} from '@mui/material';

interface DashboardProps {
  userRole: string;
}

const Dashboard: React.FC<DashboardProps> = ({ userRole }) => {
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
                  <Card variant="outlined" sx={{ p: 2 }}>
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
                  <Card variant="outlined" sx={{ p: 2 }}>
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
                  <Card variant="outlined" sx={{ p: 2 }}>
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
                  <Card variant="outlined" sx={{ p: 2 }}>
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
                    disabled
                  >
                    📝 Reportes
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    disabled
                  >
                    🗺️ Rutas
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    disabled
                  >
                    ✅ Tareas
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ py: 2 }}
                    disabled
                  >
                    📊 Estadísticas
                  </Button>
                </Grid>
              </Grid>
              <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
                Sistema con autenticación RabbitMQ integrada y gestión de roles.
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

export default Dashboard;