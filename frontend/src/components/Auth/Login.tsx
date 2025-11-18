import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Phone,
  Lock,
  Login as LoginIcon,
  PersonAdd,
  Message
} from '@mui/icons-material';

interface LoginProps {
  onLoginSuccess: (user: any, tokens: any) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [tabValue, setTabValue] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Estados para login tradicional
  const [loginForm, setLoginForm] = useState({
    identifier: '',
    password: ''
  });

  // Estados para OTP
  const [otpForm, setOtpForm] = useState({
    phone: '',
    code: '',
    step: 'phone' // 'phone' | 'code'
  });

  // Estados para registro
  const [registerForm, setRegisterForm] = useState({
    email: '',
    phone: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: ''
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError('');
    setSuccess('');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginForm),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLoginSuccess(data.user, { access: data.access, refresh: data.refresh });
      } else {
        setError(data.message || 'Error de autenticación');
      }
    } catch (err) {
      setError('Error de conexión. Verifica que el backend esté ejecutándose.');
    } finally {
      setLoading(false);
    }
  };

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
      const response = await fetch('http://localhost:8000/api/auth/register/', {
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
      const response = await fetch('http://localhost:8000/api/auth/otp/request/', {
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
      const response = await fetch('http://localhost:8000/api/auth/otp/verify/', {
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