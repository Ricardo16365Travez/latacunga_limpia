# Ciclo de Vida del Desarrollo - EPAGAL Latacunga

## Índice
1. [Metodología Ágil - Scrum](#metodologia-agil-scrum)
2. [Sprint Planning](#sprint-planning)
3. [Feature Development Workflow](#feature-development-workflow)
4. [Release Management](#release-management)
5. [Retrospectivas y Mejora Continua](#retrospectivas)

---

## Metodología Ágil - Scrum

### Estructura del Equipo

```
┌──────────────────────────────────────────────────┐
│              EQUIPO SCRUM EPAGAL                  │
├──────────────────────────────────────────────────┤
│                                                   │
│  Product Owner (1)                                │
│    └─► Define prioridades y acepta entregas      │
│                                                   │
│  Scrum Master (1)                                 │
│    └─► Facilita ceremonias y remueve blockers    │
│                                                   │
│  Development Team (3-5)                           │
│    ├─► Backend Developer (Python/FastAPI)        │
│    ├─► Frontend Developer (React/TypeScript)     │
│    ├─► Full-Stack Developer                      │
│    └─► QA Engineer (BDD/Testing)                 │
│                                                   │
└──────────────────────────────────────────────────┘
```

### Sprint Cycle (2 semanas)

```
Semana 1                         Semana 2
├─────────────────────────────┼─────────────────────────────┤
│                             │                             │
│ LUNES: Sprint Planning      │ LUNES: Daily Standup        │
│   (4 horas)                 │   (15 min)                  │
│   └─► Sprint Goal           │                             │
│   └─► Sprint Backlog        │ MARTES: Daily Standup       │
│                             │   (15 min)                  │
│ MARTES-JUEVES:              │   └─► Development           │
│   Development + Daily       │                             │
│   Standups (15 min/día)     │ MIÉRCOLES: Daily Standup    │
│                             │   (15 min)                  │
│ VIERNES:                    │   └─► Development           │
│   Backlog Refinement        │                             │
│   (2 horas)                 │ JUEVES:                     │
│                             │   Sprint Review (2 horas)   │
│                             │   Sprint Retrospective (1h) │
│                             │                             │
│                             │ VIERNES:                    │
│                             │   Documentation & Cleanup   │
│                             │   Release to Production     │
│                             │                             │
└─────────────────────────────┴─────────────────────────────┘
```

---

## Sprint Planning

### Ceremonia de Sprint Planning

**Duración**: 4 horas (para sprint de 2 semanas)

**Participantes**: Todo el equipo Scrum

**Objetivos**:
1. Definir Sprint Goal
2. Seleccionar User Stories del Product Backlog
3. Descomponer Stories en Tasks
4. Estimar esfuerzo (Story Points)
5. Comprometerse con Sprint Backlog

### Ejemplo Real: Sprint 3 - Módulo de Rutas

```markdown
# Sprint 3: Generación y Optimización de Rutas

## Sprint Goal
"Implementar generación automática de rutas optimizadas por zona con asignación de conductores"

## Team Capacity
- Backend Dev: 40 horas
- Frontend Dev: 40 horas
- Full-Stack Dev: 40 horas
- QA Engineer: 40 horas
Total: 160 horas

## Sprint Backlog (Velocity: 34 Story Points)

### User Story 1: Generación de Rutas por Zona (13 SP)
**Como**: Administrador
**Quiero**: Generar rutas optimizadas para zona oriental u occidental
**Para**: Planificar recolección eficiente de residuos

**Criterios de Aceptación**:
- [ ] Seleccionar zona (oriental/occidental)
- [ ] Sistema obtiene incidencias pendientes de la zona
- [ ] Integración con OSRM para calcular ruta óptima
- [ ] Calcular métricas: distancia, duración, camiones necesarios
- [ ] Persistir ruta y detalles en BD
- [ ] Response time < 5 segundos

**Tasks**:
- [ ] Diseñar endpoint POST /api/rutas/generar/{zona} (Backend, 4h)
- [ ] Implementar RutaService.generar_ruta() (Backend, 6h)
- [ ] Integrar OSRMService (Backend, 5h)
- [ ] Tests unitarios RutaService (Backend, 3h)
- [ ] BDD scenarios para generación de rutas (QA, 4h)
- [ ] Componente GeneracionRutas.tsx (Frontend, 5h)
- [ ] Llamada API en rutasService.ts (Frontend, 2h)
- [ ] UI para mostrar métricas de ruta (Frontend, 4h)
- [ ] Tests Jest para componente (Frontend, 3h)
- [ ] Integración completa E2E (QA, 4h)

**Total**: 40 horas, 13 Story Points

---

### User Story 2: Visualización de Ruta en Mapa (8 SP)
**Como**: Operador
**Quiero**: Ver ruta generada en mapa interactivo
**Para**: Validar orden de puntos de recolección

**Criterios de Aceptación**:
- [ ] Mapa con Leaflet mostrando ruta completa
- [ ] Marcadores numerados por orden de visita
- [ ] Línea de ruta conectando puntos
- [ ] Info tooltip al hacer hover en marcador
- [ ] Zoom automático para abarcar todos los puntos

**Tasks**:
- [ ] Componente RutaMapa.tsx con Leaflet (Frontend, 6h)
- [ ] Integración con routingMap.ts (Frontend, 4h)
- [ ] Endpoint GET /api/rutas/{id}/detalles (Backend, 3h)
- [ ] Estilización de marcadores y líneas (Frontend, 3h)
- [ ] Tests de visualización (Frontend, 2h)
- [ ] BDD scenarios para mapa (QA, 3h)

**Total**: 21 horas, 8 Story Points

---

### User Story 3: Asignación de Conductores a Ruta (13 SP)
**Como**: Administrador
**Quiero**: Asignar conductores disponibles a ruta generada
**Para**: Coordinar trabajo de campo

**Criterios de Aceptación**:
- [ ] Listar conductores disponibles por zona
- [ ] Asignar 1+ conductores a ruta
- [ ] Especificar vehículo (compactador, recolector, volqueta)
- [ ] Enviar notificación push al conductor
- [ ] Cambiar estado de ruta a "asignada"
- [ ] Conductor puede ver ruta en app móvil

**Tasks**:
- [ ] Endpoint GET /api/conductores/disponibles (Backend, 3h)
- [ ] Endpoint POST /api/rutas/{id}/asignar (Backend, 5h)
- [ ] Modelo AsignacionConductor (Backend, 2h)
- [ ] NotificationService.send_push() (Backend, 4h)
- [ ] Componente AsignacionConductores.tsx (Frontend, 6h)
- [ ] Tests unitarios asignación (Backend, 3h)
- [ ] BDD scenarios para asignación (QA, 4h)
- [ ] Integración con FCM (Firebase) (Backend, 4h)
- [ ] Vista móvil de ruta asignada (Frontend, 5h)

**Total**: 36 horas, 13 Story Points

---

## Definition of Done (DoD)

Checklist que TODA User Story debe cumplir antes de considerarse "Done":

✓ **Código**:
  - [ ] Código escrito siguiendo convenciones del proyecto
  - [ ] Code Review aprobado por al menos 1 desarrollador
  - [ ] Sin merge conflicts con branch develop
  - [ ] Commits siguen Conventional Commits

✓ **Tests**:
  - [ ] Tests unitarios escritos y pasando
  - [ ] Coverage >= 80%
  - [ ] BDD scenarios escritos y pasando
  - [ ] Tests de integración pasando
  - [ ] Sin tests flakey (intermitentes)

✓ **Documentación**:
  - [ ] Código comentado donde es necesario
  - [ ] README actualizado si aplica
  - [ ] API documentation actualizada (Swagger)
  - [ ] Changelog actualizado

✓ **Calidad**:
  - [ ] Linter pasando sin warnings
  - [ ] Sin vulnerabilidades de seguridad
  - [ ] Performance aceptable (< 500ms API, < 3s UI)
  - [ ] Responsive design validado (mobile/tablet/desktop)

✓ **Deployment**:
  - [ ] CI pipeline pasando (green build)
  - [ ] Deploy a staging exitoso
  - [ ] Smoke tests en staging pasando
  - [ ] Product Owner acepta la funcionalidad

```

---

## Feature Development Workflow

### Flujo Completo de una Feature

```
1. PLANIFICACIÓN
   ├─► Product Owner escribe User Story
   ├─► Equipo estima Story Points (Planning Poker)
   ├─► Se añade a Product Backlog
   └─► Se prioriza según valor de negocio

2. SPRINT PLANNING
   ├─► User Story se mueve a Sprint Backlog
   ├─► Se descompone en Tasks técnicos
   ├─► Se asignan responsables
   └─► Team se compromete con entrega

3. DESARROLLO
   ├─► Developer crea branch feature/US-XXX
   ├─► Escribe tests (TDD approach)
   │   └─► Red → Green → Refactor
   ├─► Implementa funcionalidad
   ├─► Commits frecuentes con mensajes claros
   └─► Push a remote branch

4. CODE REVIEW
   ├─► Abre Pull Request
   ├─► CI ejecuta tests automáticamente
   ├─► Reviewer revisa código
   ├─► Developer aplica feedback
   ├─► Approval de reviewer
   └─► Merge a develop

5. TESTING
   ├─► QA ejecuta tests manuales en staging
   ├─► BDD scenarios validados
   ├─► Bugs reportados como sub-tasks
   └─► Regression testing

6. DEMO
   ├─► Sprint Review con stakeholders
   ├─► Product Owner valida funcionalidad
   ├─► Feedback documentado
   └─► Aceptación o rechazo

7. DEPLOYMENT
   ├─► Merge develop → main
   ├─► CD pipeline despliega a producción
   ├─► Smoke tests post-deployment
   └─► Monitoreo de logs y métricas

8. RETROSPECTIVA
   ├─► ¿Qué salió bien?
   ├─► ¿Qué se puede mejorar?
   ├─► Action items para siguiente sprint
   └─► Celebrar éxitos 🎉
```

### Ejemplo Detallado: Feature "Generación de Rutas"

#### Día 1-2: Diseño y Planificación

```markdown
## Diseño Técnico

### Backend Architecture
- **Endpoint**: POST /api/rutas/generar/{zona}
- **Service**: RutaService.generar_ruta_automatica()
- **Dependencies**: OSRMService, IncidenciaRepository
- **Models**: RutaGenerada, RutaDetalle

### Frontend Architecture
- **Component**: GeneracionRutas.tsx
- **Service**: rutasService.generarRuta(zona)
- **State**: useState para loading, error, result
- **UI**: Material-UI Card, Button, CircularProgress

### Database Schema
```sql
CREATE TABLE rutas_generadas (
  id SERIAL PRIMARY KEY,
  zona VARCHAR(20) NOT NULL,
  fecha_generacion TIMESTAMP DEFAULT NOW(),
  suma_gravedad INTEGER,
  camiones_usados INTEGER,
  costo_total INTEGER,
  duracion_estimada INTERVAL,
  estado VARCHAR(20) DEFAULT 'planeada'
);

CREATE TABLE rutas_detalles (
  id SERIAL PRIMARY KEY,
  ruta_id INTEGER REFERENCES rutas_generadas(id),
  orden INTEGER NOT NULL,
  incidencia_id INTEGER REFERENCES incidencias(id),
  lat DECIMAL(10,8),
  lon DECIMAL(11,8),
  tipo_punto VARCHAR(20),
  camion_tipo VARCHAR(20)
);
```

### API Contract
```json
// Request
POST /api/rutas/generar/oriental
Authorization: Bearer <token>

// Response 201 Created
{
  "id": 15,
  "zona": "oriental",
  "fecha_generacion": "2026-01-20T10:30:00Z",
  "suma_gravedad": 42,
  "camiones_usados": 3,
  "costo_total": 15000,
  "duracion_estimada": "02:30:00",
  "estado": "planeada",
  "detalles": [
    {
      "orden": 1,
      "incidencia_id": 5,
      "lat": -0.9322,
      "lon": -78.6170,
      "tipo_punto": "incidencia",
      "camion_tipo": "compactador"
    },
    ...
  ]
}
```
```

#### Día 3-5: Desarrollo Backend

```python
# backend_prod/app/services/ruta_service.py

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Incidencia, RutaGenerada, RutaDetalle
from app.services.osrm_service import OSRMService
import logging

logger = logging.getLogger(__name__)

class RutaService:
    def __init__(self):
        self.osrm = OSRMService()
    
    def generar_ruta_automatica(
        self,
        db: Session,
        zona: str
    ) -> Optional[RutaGenerada]:
        """
        Genera ruta optimizada para una zona.
        
        Algoritmo:
        1. Obtener incidencias pendientes ordenadas por gravedad
        2. Extraer coordenadas
        3. Llamar a OSRM para optimizar orden
        4. Calcular métricas (camiones, costo, duración)
        5. Persistir ruta y detalles
        6. Actualizar estado de incidencias
        """
        logger.info(f"Generando ruta para zona: {zona}")
        
        # 1. Obtener incidencias
        incidencias = db.query(Incidencia).filter(
            Incidencia.zona == zona,
            Incidencia.estado == 'pendiente'
        ).order_by(Incidencia.gravedad.desc()).all()
        
        if not incidencias:
            logger.warning(f"No hay incidencias en zona {zona}")
            return None
        
        logger.info(f"Encontradas {len(incidencias)} incidencias")
        
        # 2. Preparar coordenadas para OSRM
        coordenadas = [(inc.lat, inc.lon) for inc in incidencias]
        
        # 3. Calcular ruta óptima
        try:
            ruta_osrm = self.osrm.calcular_ruta_optima(coordenadas)
        except Exception as e:
            logger.error(f"Error en OSRM: {e}")
            raise
        
        # 4. Calcular métricas
        suma_gravedad = sum(inc.gravedad for inc in incidencias)
        camiones = self._calcular_camiones_necesarios(suma_gravedad)
        
        # 5. Crear ruta
        nueva_ruta = RutaGenerada(
            zona=zona,
            suma_gravedad=suma_gravedad,
            camiones_usados=camiones,
            costo_total=ruta_osrm['distance'],
            duracion_estimada=timedelta(seconds=ruta_osrm['duration']),
            estado='planeada'
        )
        
        db.add(nueva_ruta)
        db.flush()
        
        # 6. Crear detalles según orden de OSRM
        for orden, idx in enumerate(ruta_osrm['waypoint_order'], 1):
            inc = incidencias[idx]
            detalle = RutaDetalle(
                ruta_id=nueva_ruta.id,
                orden=orden,
                incidencia_id=inc.id,
                lat=inc.lat,
                lon=inc.lon,
                tipo_punto='incidencia',
                camion_tipo=self._asignar_camion(inc)
            )
            db.add(detalle)
            
            # Marcar incidencia como asignada
            inc.estado = 'asignada'
        
        db.commit()
        db.refresh(nueva_ruta)
        
        logger.info(
            f"Ruta {nueva_ruta.id} creada: "
            f"{len(incidencias)} puntos, {camiones} camiones"
        )
        
        return nueva_ruta
    
    def _calcular_camiones_necesarios(self, suma_gravedad: int) -> int:
        """Calcula camiones según gravedad total."""
        CAPACIDAD_CAMION = 15  # puntos de gravedad
        return max(1, (suma_gravedad + CAPACIDAD_CAMION - 1) // CAPACIDAD_CAMION)
    
    def _asignar_camion(self, incidencia: Incidencia) -> str:
        """Asigna tipo de camión según tipo de incidencia."""
        mapping = {
            'acopio_lleno': 'compactador',
            'escombros': 'volqueta',
            'animal_muerto': 'recolector',
            'zona_critica': 'compactador'
        }
        return mapping.get(incidencia.tipo, 'recolector')
```

**Tests (TDD approach)**:

```python
# tests/test_ruta_service.py

import pytest
from app.services.ruta_service import RutaService

def test_generar_ruta_sin_incidencias(mock_db):
    """Debe retornar None si no hay incidencias."""
    mock_db.query().filter().order_by().all.return_value = []
    
    service = RutaService()
    resultado = service.generar_ruta_automatica(mock_db, 'oriental')
    
    assert resultado is None

def test_calcular_camiones_necesarios():
    """Debe calcular camiones correctamente."""
    service = RutaService()
    
    assert service._calcular_camiones_necesarios(10) == 1
    assert service._calcular_camiones_necesarios(15) == 1
    assert service._calcular_camiones_necesarios(16) == 2
    assert service._calcular_camiones_necesarios(45) == 3
```

#### Día 6-8: Desarrollo Frontend

```typescript
// frontend/src/components/Routes/GeneracionRutas.tsx

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Select,
  MenuItem
} from '@mui/material';
import { rutasService } from '../../services/rutasService';

interface RutaGenerada {
  id: number;
  zona: string;
  suma_gravedad: number;
  camiones_usados: number;
  costo_total: number;
  duracion_estimada: string;
}

const GeneracionRutas: React.FC = () => {
  const [zona, setZona] = useState<'oriental' | 'occidental'>('oriental');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ruta, setRuta] = useState<RutaGenerada | null>(null);

  const handleGenerar = async () => {
    setLoading(true);
    setError(null);
    setRuta(null);

    try {
      const resultado = await rutasService.generarRuta(zona);
      setRuta(resultado);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al generar ruta');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Generación Automática de Rutas
          </Typography>

          <Box display="flex" gap={2} alignItems="center" mb={3}>
            <Select
              value={zona}
              onChange={(e) => setZona(e.target.value as any)}
              disabled={loading}
            >
              <MenuItem value="oriental">Zona Oriental</MenuItem>
              <MenuItem value="occidental">Zona Occidental</MenuItem>
            </Select>

            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerar}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Generar Ruta'}
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {ruta && (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6">
                  Ruta #{ruta.id} Generada
                </Typography>
                <Typography>Zona: {ruta.zona}</Typography>
                <Typography>
                  Gravedad Total: {ruta.suma_gravedad} puntos
                </Typography>
                <Typography>
                  Camiones Necesarios: {ruta.camiones_usados}
                </Typography>
                <Typography>
                  Distancia: {(ruta.costo_total / 1000).toFixed(2)} km
                </Typography>
                <Typography>
                  Duración Estimada: {ruta.duracion_estimada}
                </Typography>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default GeneracionRutas;
```

#### Día 9: BDD Testing

```gherkin
# features/rutas.feature

Feature: Generación de Rutas Optimizadas
  Como administrador del sistema
  Quiero generar rutas optimizadas automáticamente
  Para planificar la recolección eficiente

  Background:
    Given el usuario admin está autenticado
    And existen las siguientes incidencias pendientes:
      | zona       | tipo          | gravedad | lat      | lon       |
      | oriental   | acopio_lleno  | 8        | -0.9322  | -78.6170  |
      | oriental   | escombros     | 6        | -0.9350  | -78.6150  |
      | oriental   | zona_critica  | 9        | -0.9300  | -78.6180  |
      | occidental | acopio_lleno  | 7        | -0.9322  | -78.6300  |

  Scenario: Generar ruta para zona con incidencias
    When genero una ruta para zona "oriental"
    Then la ruta debe ser creada exitosamente
    And la ruta debe incluir 3 incidencias
    And la suma de gravedad debe ser 23
    And se deben asignar 2 camiones
    And las incidencias deben cambiar a estado "asignada"

  Scenario: Intentar generar ruta sin incidencias
    Given no hay incidencias pendientes en zona "oriental"
    When intento generar una ruta para zona "oriental"
    Then debo recibir un mensaje "No hay incidencias pendientes"
    And no se debe crear ninguna ruta

  Scenario: Optimización de orden de visita
    When genero una ruta para zona "oriental"
    Then el orden de los puntos debe minimizar la distancia total
    And el punto con mayor gravedad debe ser visitado primero
```

#### Día 10: Code Review & Deploy

```markdown
## Pull Request: Feature/US-012-generacion-rutas

### Cambios
- ✅ Endpoint POST /api/rutas/generar/{zona}
- ✅ RutaService con integración OSRM
- ✅ Componente GeneracionRutas.tsx
- ✅ Tests unitarios (18 tests, 94% coverage)
- ✅ BDD scenarios (3 escenarios pasando)
- ✅ Documentación API actualizada

### Checklist
- [x] Code Review aprobado (@backend-dev, @frontend-dev)
- [x] CI pipeline pasando
- [x] Tests coverage >= 80%
- [x] Deploy a staging exitoso
- [x] QA manual completado
- [x] Product Owner aprueba funcionalidad

### Screenshots
[Adjuntar capturas de pantalla]

### Ready to Merge! ✅
```

---

## Release Management

### Versionamiento Semántico

```
MAJOR.MINOR.PATCH

Ejemplos:
- v1.0.0 → Primera versión estable
- v1.1.0 → Nueva funcionalidad (módulo de rutas)
- v1.1.1 → Bugfix (corregir cálculo de gravedad)
- v2.0.0 → Breaking change (nueva API authentication)
```

### Release Process

```
1. PREPARACIÓN (1 día antes)
   ├─► Crear branch release/v1.1.0 desde develop
   ├─► Bump version en package.json y __init__.py
   ├─► Actualizar CHANGELOG.md
   ├─► Ejecutar full regression testing
   └─► Crear Release Notes

2. VALIDACIÓN (Día del release)
   ├─► Deploy a staging
   ├─► Smoke tests en staging
   ├─► Performance testing
   ├─► Security scan
   └─► Sign-off de Product Owner

3. DEPLOYMENT (Ventana de mantenimiento)
   ├─► Backup de base de datos producción
   ├─► Ejecutar database migrations
   ├─► Merge release → main
   ├─► CI/CD despliega automáticamente
   ├─► Smoke tests en producción
   └─► Crear Git tag v1.1.0

4. POST-DEPLOYMENT (1 hora después)
   ├─► Monitorear logs y métricas
   ├─► Validar funcionalidades críticas
   ├─► Notificar a stakeholders
   └─► Merge release → develop

5. ROLLBACK (Si algo falla)
   ├─► Revertir deploy en Render
   ├─► Restaurar backup de BD
   ├─► Notificar equipo
   └─► Investigar causa raíz
```

---

## Retrospectivas y Mejora Continua

### Formato de Retrospectiva

```
┌──────────────────────────────────────────────────┐
│         RETROSPECTIVA SPRINT 3                    │
├──────────────────────────────────────────────────┤
│                                                   │
│  1. ¿Qué salió BIEN? (Keep Doing) 😊            │
│     ✓ Tests BDD mejoraron comunicación           │
│     ✓ Code reviews más rápidos (<2 horas)       │
│     ✓ Deploy sin incidentes                      │
│                                                   │
│  2. ¿Qué salió MAL? (Stop Doing) 😞             │
│     ✗ Merge conflicts frecuentes                 │
│     ✗ Falta de documentación técnica             │
│     ✗ Tests corriendo muy lentos (15 min)        │
│                                                   │
│  3. ¿Qué MEJORAR? (Start Doing) 💡              │
│     → Sync diarios de branches                    │
│     → Template de documentación técnica           │
│     → Paralelizar tests en CI                     │
│                                                   │
│  4. ACTION ITEMS (Responsable, Deadline)          │
│     • Crear guía de branching (@scrum-master, 2d)│
│     • Optimizar suite de tests (@qa, 1w)         │
│     • Workshop de Git (@tech-lead, next sprint)  │
│                                                   │
└──────────────────────────────────────────────────┘
```

### Métricas de Mejora Continua

```
Sprint Velocity (Story Points completados):
Sprint 1: 21 SP
Sprint 2: 28 SP
Sprint 3: 34 SP ← Incremento sostenido 📈

Code Coverage:
Sprint 1: 72%
Sprint 2: 79%
Sprint 3: 87% ← Mejora continua ✅

Deployment Frequency:
Sprint 1: 2 deploys
Sprint 2: 4 deploys
Sprint 3: 6 deploys ← Más frecuente 🚀

Bug Escape Rate (bugs en producción):
Sprint 1: 5 bugs
Sprint 2: 2 bugs
Sprint 3: 1 bug ← Menos bugs 🐛
```

---

**Conclusión:**

El ciclo de vida de desarrollo en EPAGAL está optimizado para:
- ✅ Entregas frecuentes y predecibles
- ✅ Alta calidad de código
- ✅ Feedback rápido
- ✅ Mejora continua
- ✅ Transparencia total con stakeholders