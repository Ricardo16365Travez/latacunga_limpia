/**
 * Servidor Express para servir la aplicación React en producción
 * Maneja el SPA routing redirigiendo todas las rutas no-estáticas a index.html
 */
const express = require('express');
const path = require('path');
const app = express();

// Directorio de archivos estáticos (build de React)
const buildPath = path.join(__dirname, 'build');

// Middleware para logging (PRIMERO)
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Middleware para servir archivos estáticos
// Archivos con extensión (js, css, png, etc) se sirven directamente
app.use(express.static(buildPath, {
  maxAge: '1d',
  etag: false,
  setHeaders: (res, path) => {
    // Cache largo para archivos con hash
    if (path.match(/\.[0-9a-f]{8}\.(js|css)$/)) {
      res.set('Cache-Control', 'public, max-age=31536000, immutable');
    }
    // No cachear HTML
    if (path.endsWith('.html')) {
      res.set('Cache-Control', 'public, max-age=0, must-revalidate');
    }
  }
}));

// SPA Routing: Catch-all para rutas sin extensión
// Redirige a index.html para que React Router maneje la navegación
// Las llamadas a /api/** van directamente a través de axios al backend (no pasan por aquí)
app.get('*', (req, res) => {
  const indexPath = path.join(buildPath, 'index.html');
  console.log(`[SPA] Serving: ${req.path} -> index.html`);
  
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error(`[ERROR] Failed to serve index.html: ${err.message}`);
      try {
        const fs = require('fs');
        const html = fs.readFileSync(indexPath, 'utf8');
        res.set('Content-Type', 'text/html');
        res.send(html);
      } catch (readErr) {
        console.error(`[CRITICAL] Could not read index.html: ${readErr.message}`);
        res.status(500).send('Could not load application');
      }
    }
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(`[ERROR] ${err.message}`);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Iniciar servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Servidor React ejecutándose en puerto ${PORT}`);
  console.log(`📁 Sirviendo archivos desde: ${buildPath}`);
  console.log(`🔄 SPA routing habilitado: todas las rutas van a index.html`);
});
