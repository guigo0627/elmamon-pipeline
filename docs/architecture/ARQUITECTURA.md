# 🏗️ Arquitectura - elmamon-pipeline

## Visión General

Pipeline modular de generación automática de videos cortos, diseñado para escalar desde validación (Fase 1) hasta producción masiva (Fase 3) sin refactorización mayor.

## Principios de Diseño

### 1. Modularidad por etapas
Cada etapa del pipeline es independiente y puede ejecutarse/testearse por separado.

### 2. Estado persistente
Todos los outputs intermedios se guardan, permitiendo:
- Debugging granular por etapa
- Reintentos parciales sin regenerar todo
- Continuación de sesiones interrumpidas

### 3. Configuración externalizada
- Prompts en archivos `.txt` editables sin tocar código
- Especificaciones visuales en JSON versionable
- Variables de entorno para credenciales y configuración

### 4. Escalabilidad horizontal
Preparado para:
- Procesamiento en paralelo (Fase 3)
- Múltiples workers
- Cola de trabajos
- Cache de assets recurrentes

---

## Estructura del Proyecto

```
elmamon-pipeline/
│
├── CONTEXTO.md                    # Estado actual, próximos pasos, roadmap
├── .env                           # Credenciales (no versionado)
├── .env.template                  # Plantilla de configuración
├── requirements.txt               # Dependencias Python
├── pipeline.py                    # Orquestador principal
│
├── docs/                          # 📚 Documentación centralizada
│   ├── README.md                  # Documentación completa del proyecto
│   ├── architecture/              # Documentación de arquitectura
│   │   └── ARQUITECTURA.md        # Este archivo
│   ├── guides/                    # Guías de usuario
│   │   └── INICIO_RAPIDO.md       # Quick start
│   ├── specs/                     # Especificaciones y configuraciones
│   │   ├── requerimientos-originales.md
│   │   └── style_bible.json       # Guía de estilo visual
│   └── prompts/                   # Prompts de IA (versionados)
│       ├── prompt_guion.txt
│       └── prompt_validador.txt
│
├── scripts/                       # 🔧 Scripts del pipeline
│   ├── utils.py                   # Utilidades compartidas
│   ├── 01_guion.py               # Etapa 1: Generación de guion
│   ├── 02_validador.py           # Etapa 1.5: Validación de guion
│   ├── 03_imagenes.py            # Etapa 2: Generación de imágenes (TODO)
│   ├── 04_audio.py               # Etapa 3: Generación de audio (TODO)
│   ├── 05_animacion.py           # Etapa 4: Animación (TODO)
│   ├── 06_montaje.py             # Etapa 5: Montaje (TODO)
│   ├── 07_subtitulos.py          # Etapa 6: Subtítulos (TODO)
│   ├── 08_publicacion.py         # Etapa 7: Publicación (Fase 2+)
│   └── test_setup.py             # Verificador de configuración
│
├── assets_temp/                   # 💾 Outputs intermedios (por sesión)
│   ├── guiones/                   # JSONs de guiones y validaciones
│   ├── imagenes/                  # PNGs de personajes, fondos, cutaways
│   ├── audio/                     # MP3s de voces por personaje
│   └── animaciones/               # MP4s de personajes animados
│
├── output/                        # 🎬 Videos finales listos para publicar
│
├── logs/                          # 📝 Logs estructurados por sesión
│   └── {session_id}.json
│
└── temp/                          # 🗑️ Archivos temporales desechables
    └── (ignorado en git)
```

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE COMPLETO                         │
└─────────────────────────────────────────────────────────────────┘

INPUT: tema opcional (string) o aleatorio
  │
  ├─► [1] GUION (Claude API)
  │     └─► guion.json → assets_temp/guiones/
  │           │
  │           ├─► [1.5] VALIDADOR (Claude API)
  │           │     ├─► aprobado? ✓ → continuar
  │           │     └─► rechazado? ✗ → reescribir (max 2x)
  │           │
  │           ├─► personajes[] (roles + especie mascota)
  │           ├─► escenario (sala/cocina/jardín/etc)
  │           ├─► dialogo[] (hablante + linea + cutaways?)
  │           └─► duracion_estimada_seg
  │
  ├─► [2] IMÁGENES (Replicate: Flux/Ideogram) [TODO]
  │     ├─► personajes.png × N
  │     ├─► fondo.png
  │     └─► cutaways.png × N
  │           └─► assets_temp/imagenes/
  │
  ├─► [3] AUDIO (ElevenLabs) [TODO]
  │     ├─► voz_personaje1.mp3 + alignment.json
  │     ├─► voz_personaje2.mp3 + alignment.json
  │     └─► voz_personaje3.mp3 + alignment.json
  │           └─► assets_temp/audio/
  │
  ├─► [4] ANIMACIÓN (Hedra) [TODO]
  │     ├─► personaje1_animado.mp4
  │     ├─► personaje2_animado.mp4
  │     └─► personaje3_animado.mp4
  │           └─► assets_temp/animaciones/
  │
  ├─► [5] CUTAWAYS ANIMADOS (ffmpeg Ken Burns) [TODO]
  │     └─► cutaway_X_animado.mp4
  │
  ├─► [6] MONTAJE (ffmpeg) [TODO]
  │     └─► video_sin_subtitulos.mp4
  │
  ├─► [7] SUBTÍTULOS (ffmpeg + alignment) [TODO]
  │     └─► video_final.mp4 → output/
  │
  └─► [8] PUBLICACIÓN (n8n + APIs) [Fase 2+]
        ├─► Facebook Reels (Meta Graph API)
        └─► YouTube Shorts (YouTube Data API)

OUTPUT: video_final.mp4 (1080x1920, ≤30s, H.264)
```

---

## Componentes Principales

### 1. Orquestador (`pipeline.py`)

**Responsabilidades:**
- Ejecutar etapas secuencialmente
- Gestionar sesiones (session_id con timestamp)
- Manejo de errores y reintentos
- Logging centralizado
- CLI para control manual

**Interfaz:**
```bash
python pipeline.py [--tema "texto"] [--hasta-etapa N] [--continuar SESSION_ID]
```

### 2. Módulo de Utilidades (`scripts/utils.py`)

**Funciones clave:**
- `setup_logger()` - Logger con colores
- `get_session_id()` - ID único por corrida
- `load_prompt()` - Carga prompts desde docs/prompts/
- `load_style_bible()` - Carga specs visuales
- `log_to_file()` - Persistencia de logs por etapa
- `check_fase()` - Detección de fase del proyecto

**Variables de entorno:**
- `FASE_ACTUAL` - 1=Validación, 2=Lanzamiento, 3=Escalado
- APIs keys para todos los servicios

### 3. Scripts por Etapa

Cada script sigue el patrón:

```python
def procesar_etapa(session_id: str, input_data: dict) -> dict:
    """
    Procesa una etapa específica del pipeline
    
    Args:
        session_id: ID único de la sesión
        input_data: Datos de entrada (output de etapa anterior)
    
    Returns:
        dict: Resultado de esta etapa + metadata
    
    Raises:
        PipelineError: Si falla la etapa
    """
    logger.info(f"Iniciando Etapa X para sesión {session_id}")
    
    # 1. Validar inputs
    # 2. Llamar a API externa / procesar
    # 3. Guardar outputs en assets_temp/
    # 4. Log detallado
    # 5. Retornar resultado estructurado
    
    log_to_file(session_id, "etapa_X", result)
    return result
```

---

## Escalabilidad por Fase

### Fase 1 - Validación (ACTUAL)
```python
CONCURRENCIA = 1  # Secuencial
STORAGE = "local"  # assets_temp/ en disco
QUEUE = None      # Sin cola
CACHE = None      # Sin cache
```

### Fase 2 - Lanzamiento
```python
CONCURRENCIA = 1              # Sigue secuencial
STORAGE = "local"             # Sigue local
QUEUE = "n8n_scheduler"       # Cola de publicación
CACHE = "assets_recurrentes"  # Personajes reutilizables
```

### Fase 3 - Escalado
```python
CONCURRENCIA = 4-8            # Paralelo con ThreadPoolExecutor
STORAGE = "cloud_s3"          # S3/Cloud Storage
QUEUE = "redis_celery"        # Cola distribuida
CACHE = "redis"               # Cache distribuido
WORKERS = "multiple_machines" # Múltiples instancias
```

---

## Patrones de Diseño Aplicados

### 1. Pipeline Pattern
Cada etapa es una transformación pura: `input → process → output`

### 2. Checkpoint Pattern
Cada etapa guarda su output, permitiendo reintentos sin rehacer todo.

### 3. Strategy Pattern
APIs intercambiables (ej: Flux vs Ideogram vs DALL-E) sin cambiar lógica.

### 4. Observer Pattern
Logging centralizado observa todas las etapas.

### 5. Template Method Pattern
Todos los scripts siguen la misma estructura:
- Validar inputs
- Procesar
- Guardar outputs
- Log

---

## Gestión de Estado

### Session ID
Formato: `YYYYMMDD_HHMMSS`
Ejemplo: `20260904_214530`

**Asocia:**
- Todos los assets de una corrida
- Logs detallados
- Permite debugging post-mortem

### Estructura de Logs
```json
{
  "session_id": "20260904_214530",
  "created_at": "2026-09-04T21:45:30",
  "stages": {
    "01_guion": {
      "timestamp": "2026-09-04T21:45:32",
      "data": {
        "status": "success",
        "guion_path": "...",
        "tokens_used": 1234
      }
    },
    "02_validador_intento1": {...},
    "03_imagenes": {...}
  }
}
```

---

## Manejo de Errores

### Jerarquía de Excepciones
```python
Exception
└── PipelineError                    # Base
    ├── APIError                     # Fallo de API externa
    │   ├── ClaudeAPIError
    │   ├── ReplicateAPIError
    │   ├── ElevenLabsAPIError
    │   └── HedraAPIError
    ├── ValidationError              # Fallo de validación
    └── ConfigError                  # Fallo de configuración
```

### Estrategias de Retry
```python
# Etapa 1: Guion
RETRY_STRATEGY = "regenerate"  # Genera nuevo guion
MAX_RETRIES = 3

# Etapa 1.5: Validador
RETRY_STRATEGY = "rewrite"     # Reescribe basándose en feedback
MAX_RETRIES = 2

# Etapa 2-7: Assets
RETRY_STRATEGY = "exponential_backoff"
MAX_RETRIES = 5
BACKOFF_FACTOR = 2
```

---

## Seguridad

### Secrets Management
- ✅ Todas las API keys en `.env` (nunca en código)
- ✅ `.env` en `.gitignore`
- ✅ `.env.template` con ejemplos
- ✅ Validación de keys al inicio

### Rate Limiting
```python
RATE_LIMITS = {
    "claude": {"requests_per_minute": 50},
    "replicate": {"requests_per_minute": 10},
    "elevenlabs": {"characters_per_month": 10000},  # Free tier
    "hedra": {"videos_per_month": 7}                # Free tier
}
```

### Asset Cleanup
- `assets_temp/` se limpia periódicamente
- `output/` se mantiene indefinidamente
- `logs/` se archivan mensualmente

---

## Testing Strategy

### Fase 1 (Actual)
- ✅ `test_setup.py` - Verifica configuración
- Manual testing de cada etapa

### Fase 2
- Unit tests por script
- Integration tests end-to-end
- Fixtures con guiones de prueba

### Fase 3
- Load testing
- Stress testing
- CI/CD pipeline

---

## Métricas y Observabilidad

### Métricas por Etapa
```python
{
    "etapa": "01_guion",
    "duracion_segundos": 3.2,
    "tokens_consumidos": 1234,
    "costo_usd": 0.015,
    "intentos": 1,
    "status": "success"
}
```

### KPIs del Pipeline
- Tiempo total por video
- Costo total por video
- Tasa de aprobación de guiones
- Tasa de error por etapa

---

## Roadmap Técnico

### ✅ Completado
- [x] Estructura base modular
- [x] Sistema de logging
- [x] Gestión de sesiones
- [x] Etapa 1: Guion
- [x] Etapa 1.5: Validación

### 🚧 En Desarrollo
- [ ] Etapa 2: Generación de imágenes
- [ ] Etapa 3: Generación de audio
- [ ] Etapa 4: Animación
- [ ] Etapa 5-6: Montaje
- [ ] Etapa 7: Subtítulos

### 🔮 Futuro (Fase 2+)
- [ ] Etapa 8: Publicación automática
- [ ] Cache de assets recurrentes
- [ ] Procesamiento en paralelo
- [ ] Queue system (Redis/Celery)
- [ ] Cloud storage (S3)
- [ ] Dashboard de monitoreo
- [ ] API REST para control externo

---

**Última actualización:** 2026-09-04  
**Versión de arquitectura:** 1.0 (Fase 1)
