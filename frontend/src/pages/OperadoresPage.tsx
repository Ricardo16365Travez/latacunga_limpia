import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import api from '../services/apiService';
import { API_ENDPOINTS } from '../config/api';

interface Operador {
  id: string | number;
  email: string;
  username: string;
  phone: string | null;
  display_name: string; // Mapeado desde nombre_completo
  licencia_tipo?: string | null;
  zona_preferida?: string | null;
}

export default function OperadoresPage() {
  const [operadores, setOperadores] = useState<Operador[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState<string | number | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    phone: '',
    display_name: '',
  });

  // Cargar operadores
  useEffect(() => {
    cargarOperadores();
  }, []);

  const cargarOperadores = async () => {
    try {
      setLoading(true);
      // Usar endpoint de CONDUCTORES, que sí existe en backend
      const { data } = await api.get(API_ENDPOINTS.CONDUCTORES.LISTAR);
      const lista: Operador[] = (Array.isArray(data) ? data : (data?.results || []))
        .map((c: any) => ({
          id: c.id,
          email: c.email || '',
          username: c.username || '',
          phone: c.telefono || null,
          display_name: c.nombre_completo || c.display_name || '',
          licencia_tipo: c.licencia_tipo || null,
          zona_preferida: c.zona_preferida || null,
        }));
      setOperadores(lista);
      setError(null);
    } catch (err: any) {
      setError('Error al cargar operadores');
      setOperadores([]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (operador?: Operador) => {
    if (operador) {
      setEditingId(operador.id);
      setFormData({
        email: operador.email,
        username: operador.username,
        password: '',
        phone: operador.phone || '',
        display_name: operador.display_name,
      });
    } else {
      setEditingId(null);
      setFormData({
        email: '',
        username: '',
        password: '',
        phone: '',
        display_name: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingId(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    try {
      const payload = {
        email: formData.email,
        username: formData.username,
        password: formData.password || 'operador123',
        nombre_completo: formData.display_name,
        telefono: formData.phone || null,
        licencia_tipo: 'C',
        zona_preferida: 'oriental',
      };
      if (editingId !== null) {
        await api.patch(API_ENDPOINTS.CONDUCTORES.ACTUALIZAR(editingId), payload);
      } else {
        await api.post(API_ENDPOINTS.CONDUCTORES.CREAR, payload);
      }
      await cargarOperadores();
      handleCloseDialog();
    } catch (err: any) {
      setError('Error al guardar operador');
      console.error(err);
    }
  };

  const handleDelete = async (id: string | number) => {
    if (window.confirm('¿Está seguro de que desea eliminar este operador?')) {
      try {
        await api.delete(API_ENDPOINTS.CONDUCTORES.ELIMINAR(id));
        await cargarOperadores();
      } catch (err: any) {
        setError('Error al eliminar operador');
        console.error(err);
      }
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Gestión de Operadores
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nuevo Operador
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell><strong>Nombre</strong></TableCell>
              <TableCell><strong>Email</strong></TableCell>
              <TableCell><strong>Usuario</strong></TableCell>
              <TableCell><strong>Teléfono</strong></TableCell>
              <TableCell><strong>Licencia</strong></TableCell>
              <TableCell><strong>Zona</strong></TableCell>
              <TableCell align="right"><strong>Acciones</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {operadores.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  No hay operadores registrados
                </TableCell>
              </TableRow>
            ) : (
              operadores.map((operador) => (
                <TableRow key={operador.id} hover>
                  <TableCell>{operador.display_name}</TableCell>
                  <TableCell>{operador.email}</TableCell>
                  <TableCell>{operador.username}</TableCell>
                  <TableCell>{operador.phone || 'N/A'}</TableCell>
                  <TableCell>{operador.licencia_tipo || 'N/A'}</TableCell>
                  <TableCell>{operador.zona_preferida || 'N/A'}</TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      color="primary"
                      startIcon={<EditIcon />}
                      onClick={() => handleOpenDialog(operador)}
                      sx={{ mr: 1 }}
                    >
                      Editar
                    </Button>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDelete(operador.id)}
                    >
                      Eliminar
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog para crear/editar operador */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId !== null ? 'Editar Operador' : 'Nuevo Operador'}</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <TextField
            fullWidth
            label="Nombre"
            name="display_name"
            value={formData.display_name}
            onChange={handleInputChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Usuario"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            margin="normal"
          />
          {editingId === null && (
            <TextField
              fullWidth
              label="Contraseña"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              margin="normal"
            />
          )}
          <TextField
            fullWidth
            label="Teléfono"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button onClick={handleSave} variant="contained" color="primary">
            Guardar
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
