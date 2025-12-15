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
  onLoginSuccess: (user: any, tokens: any) => void;

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

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (registerForm.password !== registerForm.password_confirm) {
      setError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.REGISTER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerForm),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Usuario registrado exitosamente');
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLoginSuccess(data.user, data.tokens);
      } else {
        setError(data.message || 'Error en el registro');
      }
    } catch (err) {
      setError('Error de conexión. Verifica que el backend esté ejecutándose.');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.OTP_REQUEST, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          phone: otpForm.phone, 
          purpose: 'LOGIN' 
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Código OTP enviado a ${otpForm.phone}`);
        setOtpForm(prev => ({ ...prev, step: 'code' }));
        
        // En desarrollo, mostrar el código
        if (data.debug_code) {
          setSuccess(`Código OTP enviado: ${data.debug_code} (solo desarrollo)`);
        }
      } else {
        setError(data.message || 'Error enviando OTP');
      }
    } catch (err) {
      setError('Error de conexión. Verifica que el backend esté ejecutándose.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.OTP_VERIFY, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: otpForm.phone,
          code: otpForm.code,
          purpose: 'LOGIN'
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLoginSuccess(data.user, data.tokens);
      } else {
        setError(data.message || 'Código OTP inválido');
      }
    } catch (err) {
      setError('Error de conexión. Verifica que el backend esté ejecutándose.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: '#f5f5f5', p: 2 }}
    >
      <Card sx={{ maxWidth: 500, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center" color="primary">
            🗂️ Gestión de Residuos
          </Typography>
          <Typography variant="h6" gutterBottom align="center" color="text.secondary">
            Latacunga
          </Typography>

          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<LoginIcon />} label="Iniciar Sesión" />
            <Tab icon={<Message />} label="OTP" />
            <Tab icon={<PersonAdd />} label="Registro" />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          {/* Login tradicional */}
          <TabPanel value={tabValue} index={0}>
            <form onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Email o Teléfono"
                value={loginForm.identifier}
                onChange={(e) => setLoginForm(prev => ({ ...prev, identifier: e.target.value }))}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      {loginForm.identifier.includes('@') ? <Email /> : <Phone />}
                    </InputAdornment>
                  ),
                }}
              />
              <TextField
                fullWidth
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                value={loginForm.password}
                onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
              >
                {loading ? 'Iniciando...' : 'Iniciar Sesión'}
              </Button>
            </form>
          </TabPanel>

          {/* Login con OTP */}
          <TabPanel value={tabValue} index={1}>
            {otpForm.step === 'phone' ? (
              <form onSubmit={handleRequestOTP}>
                <TextField
                  fullWidth
                  label="Número de Teléfono"
                  value={otpForm.phone}
                  onChange={(e) => setOtpForm(prev => ({ ...prev, phone: e.target.value }))}
                  margin="normal"
                  required
                  placeholder="+593987654321"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Phone />
                      </InputAdornment>
                    ),
                  }}
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <Message />}
                >
                  {loading ? 'Enviando...' : 'Enviar Código OTP'}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleVerifyOTP}>
                <TextField
                  fullWidth
                  label="Código OTP"
                  value={otpForm.code}
                  onChange={(e) => setOtpForm(prev => ({ ...prev, code: e.target.value }))}
                  margin="normal"
                  required
                  placeholder="123456"
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
                >
                  {loading ? 'Verificando...' : 'Verificar Código'}
                </Button>
                <Button
                  fullWidth
                  variant="text"
                  onClick={() => setOtpForm(prev => ({ ...prev, step: 'phone', code: '' }))}
                >
                  Volver
                </Button>
              </form>
            )}
          </TabPanel>

          {/* Registro */}
          <TabPanel value={tabValue} index={2}>
            <form onSubmit={handleRegister}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, email: e.target.value }))}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Teléfono"
                value={registerForm.phone}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, phone: e.target.value }))}
                margin="normal"
                placeholder="+593987654321"
              />
              <TextField
                fullWidth
                label="Nombre"
                value={registerForm.first_name}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, first_name: e.target.value }))}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Apellido"
                value={registerForm.last_name}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, last_name: e.target.value }))}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Contraseña"
                type="password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, password: e.target.value }))}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Confirmar Contraseña"
                type="password"
                value={registerForm.password_confirm}
                onChange={(e) => setRegisterForm(prev => ({ ...prev, password_confirm: e.target.value }))}
                margin="normal"
                required
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <PersonAdd />}
              >
                {loading ? 'Registrando...' : 'Registrarse'}
              </Button>
            </form>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;