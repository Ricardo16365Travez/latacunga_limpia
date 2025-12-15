import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Box,
} from '@mui/material';
import {
  AccountCircle,
  ExitToApp,
  Menu as MenuIcon,
} from '@mui/icons-material';
import Login from './components/Auth/Login';
import { API_ENDPOINTS } from './config/api';
import Dashboard from './components/Layout/Dashboard';
import Sidebar from './components/Layout/Sidebar';
import IncidentsPage from './components/Incidents/IncidentsPage';
import RoutesPage from './components/Routes/RoutesPage';
import MisRutas from './components/Routes/MisRutas';
import RutaDetalle from './components/Routes/RutaDetalle';
import TasksPage from './components/Tasks/TasksPage';
import NotificationsPage from './components/Notifications/NotificationsPage';
import ReportsPage from './components/Reports/ReportsPage';

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

interface User {
  id: number;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  useEffect(() => {
    // Verificar si hay un usuario logueado al cargar la app
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
        return;
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.clear();
      }
    }

    // Auto-login de desarrollo: si estamos en localhost y no hay token,
    // intentar iniciar sesión con el admin de prueba (solo para entorno local).
    const host = window.location.hostname;
    const isLocal = host === 'localhost' || host === '127.0.0.1';

        if (isLocal && !token) {
      (async () => {
        try {
          const resp = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier: 'admin@latacunga.gob.ec', password: 'admin123' }),
          });

          if (!resp.ok) return;
          const data = await resp.json();
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          localStorage.setItem('user', JSON.stringify(data.user));
          setUser(data.user);
        } catch (e) {
          // No bloquear la app si falla el auto-login
          console.warn('Auto-login failed:', e);
        }
      })();
    }
  }, []);

  const handleLoginSuccess = (userData: User, tokens: any) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setAnchorEl(null);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />

        {!user ? (
          <Login onLoginSuccess={handleLoginSuccess} />
        ) : (
          <Box sx={{ display: 'flex' }}>
            <AppBar
              position="fixed"
              sx={{
                width: { sm: `calc(100% - 240px)` },
                ml: { sm: `240px` },
              }}
            >
              <Toolbar>
                <IconButton
                  color="inherit"
                  edge="start"
                  onClick={handleDrawerToggle}
                  sx={{ mr: 2, display: { sm: 'none' } }}
                >
                  <MenuIcon />
                </IconButton>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  🗂️ Gestión de Residuos Latacunga
                </Typography>
                <Typography variant="body2" sx={{ mr: 2 }}>
                  {user.first_name} {user.last_name} ({user.role})
                </Typography>
                <IconButton
                  size="large"
                  edge="end"
                  color="inherit"
                  onClick={handleMenuClick}
                >
                  <AccountCircle />
                </IconButton>
                <Menu
                  id="menu-appbar"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleLogout}>
                    <ExitToApp sx={{ mr: 1 }} />
                    Cerrar Sesión
                  </MenuItem>
                </Menu>
              </Toolbar>
            </AppBar>
            
            <Sidebar mobileOpen={mobileOpen} onDrawerToggle={handleDrawerToggle} />
            
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                p: 3,
                width: { sm: `calc(100% - 240px)` },
                mt: 8,
              }}
            >
              <Routes>
                <Route path="/dashboard" element={<Dashboard userRole={user?.role || 'conductor'} />} />
                <Route path="/rutas" element={<MisRutas />} />
                <Route path="/rutas/:rutaId" element={<RutaDetalle />} />
                <Route path="/routes" element={<RoutesPage />} />
                <Route path="/incidents" element={<IncidentsPage />} />
                <Route path="/tasks" element={<TasksPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Box>
          </Box>
        )}

      </ThemeProvider>
    </Router>
  );
}

export default App;