import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/apiService';
import { API_ENDPOINTS } from '../../config/api';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Paper,
} from '@mui/material';

interface LoginProps {
  onLoginSuccess?: (user: any, tokens: any) => void;
}

export default function LoginComponent(props: LoginProps = {}) {
  const { onLoginSuccess } = props;
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      // Enviar como JSON con ambos campos (identifier y username) para compatibilidad
      const ident = username.trim();
      const payload = {
        identifier: ident,
        username: ident,
        password,
      };

      const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, payload, {
        headers: { 'Content-Type': 'application/json' },
      });

      const { access_token, access, user } = response.data;
      const token = access_token || access;
      
      // Guardar token y datos del usuario
      localStorage.setItem('access_token', token);
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user || { username }));

      if (onLoginSuccess) {
        onLoginSuccess(user || { username }, { access_token: token });
      }

      // Navegar al dashboard después del login exitoso
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      // Normalizar mensajes de error (FastAPI envía detail con arrays)
      const detail = err?.response?.data?.detail;
      let message = 'Error al iniciar sesión';

      if (Array.isArray(detail)) {
        message = detail
          .map((d: any) => d?.msg || d?.detail || JSON.stringify(d))
          .join(' | ');
      } else if (typeof detail === 'string') {
        message = detail;
      }

      setError(message);
      console.error('Login error:', message, err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 2 }}>
            🗑️ EPAGAL Latacunga
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Sistema de Gestión de Rutas y Residuos
          </Typography>
        </Box>

        <Card sx={{ mb: 3, bgcolor: '#e3f2fd' }}>
          <CardContent>
            <Typography variant="body2">
              <strong>Credenciales de prueba:</strong>
              <br />
              🔐 admin / admin123
            </Typography>
          </CardContent>
        </Card>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Usuario"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            disabled={loading}
            autoFocus
          />

          <TextField
            fullWidth
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            disabled={loading}
          />

          <Button
            fullWidth
            variant="contained"
            color="primary"
            size="large"
            sx={{ mt: 3 }}
            type="submit"
            disabled={loading || !username || !password}
          >
            {loading ? <CircularProgress size={24} /> : 'Iniciar Sesión'}
          </Button>
        </form>

        <Typography variant="caption" color="textSecondary" sx={{ mt: 3, display: 'block', textAlign: 'center' }}>
          Conectando a: {process.env.REACT_APP_API_URL || 'https://tesis-c5yj.onrender.com'}
        </Typography>
      </Paper>
    </Container>
  );
}
 