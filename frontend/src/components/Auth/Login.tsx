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

export default function LoginComponent({ onLoginSuccess }: LoginProps) {
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

      const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, {
        username,
        password,
      });

      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', username);

      if (onLoginSuccess) {
        onLoginSuccess({ username }, { access_token });
      }

      navigate('/rutas');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error al iniciar sesión');
      console.error('Login error:', err);
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
              <strong>Operadores de prueba:</strong>
              <br />
              👤 operador1 / operador123
              <br />
              👤 operador2 / operador123
              <br />
              👤 operador3 / operador123
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
          Conectando a: {process.env.REACT_APP_API_URL || 'https://epagal-backend-routing-latest.onrender.com/api'}
        </Typography>
      </Paper>
    </Container>
  );
}
 