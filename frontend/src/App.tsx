import React from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Card,
  CardContent,
  Grid,
  Button
} from '@mui/material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32', // Verde para tema ambiental
    },
    secondary: {
      main: '#ff6f00', // Naranja para alertas
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🗂️ Gestión de Residuos Latacunga
            </Typography>
          </Toolbar>
        </AppBar>
        
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
                    gestionar tareas operativas de recolección y limpieza, y optimizar el 
                    control administrativo del servicio de aseo urbano en Latacunga, Ecuador.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    🏛️ Panel de Administración
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Accede al panel de administración de Django para gestionar usuarios y configuraciones.
                  </Typography>
                  <Button 
                    variant="contained" 
                    color="primary"
                    onClick={() => window.open('http://localhost:8000/admin', '_blank')}
                  >
                    Ir a Admin
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    📚 Documentación API
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Explora la documentación interactiva de la API REST del sistema.
                  </Typography>
                  <Button 
                    variant="outlined" 
                    color="primary"
                    onClick={() => window.open('http://localhost:8000/api/docs', '_blank')}
                  >
                    Ver API Docs
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              🏗️ Estado del Sistema
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Backend</Typography>
                    <Typography variant="body2">✅ Funcionando</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Frontend</Typography>
                    <Typography variant="body2">✅ Funcionando</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6">Base de Datos</Typography>
                    <Typography variant="body2">✅ PostgreSQL + PostGIS</Typography>
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
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;