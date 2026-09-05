# elmamon-pipeline

Pipeline automatizado para generar videos cortos (Reels/Shorts) de comedia familiar con mascotas antropomorfizadas, completamente sin intervención manual.

## 🎯 Objetivo

Generar videos de 30 segundos donde una mascota (perro, gato o loro) interactúa con miembros de una familia en situaciones cotidianas, con humor universal (10-12 años hasta adultos) y reconocimiento familiar ("así es mi papá/mamá", "eso me pasó a mí").

## 📋 Fase actual: 1 - Validación

**Objetivo de esta fase:** Generar videos de prueba con planes gratuitos para validar calidad visual y narrativa antes de invertir en licencias pagas.

- ❌ Sin publicación automática en redes (se activa en Fase 2)
- ✓ Uso de planes gratuitos/básicos de todas las APIs
- ✓ Capacidad: ~10 videos de prueba/mes
- ✓ Costo fijo: $0 (solo consumo mínimo de Claude API)

## 🏗️ Arquitectura del pipeline

```
[1] Guion + elenco + cutaways (Claude API)
     ↓
[1.5] Validador de guion (4 criterios de calidad)
     ↓
[2] Diseño de personajes y fondo (Replicate: Flux/Ideogram)
     ↓
[3] Audio por personaje (ElevenLabs)
     ↓
[4] Animación con lip-sync (Hedra)
     ↓
[5] Cutaways animados (ffmpeg Ken Burns)
     ↓
[6] Montaje final (ffmpeg)
     ↓
[7] Subtítulos karaoke (ElevenLabs alignment + ffmpeg)
     ↓
[8] Publicación automática (Fase 2+) - NO ACTIVA AÚN
```

## 🛠️ Instalación

### 1. Requisitos previos

- **Python 3.10+**
- **ffmpeg** instalado y en PATH
  - Windows: `winget install ffmpeg` o descargar desde [ffmpeg.org](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - Mac: `brew install ffmpeg`

### 2. Clonar y configurar

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Copiar plantilla de configuración
cp .env.template .env

# Editar .env con tus API keys
# (ver sección de APIs necesarias abajo)
```

### 3. APIs necesarias (Fase 1)

#### ✅ Obligatorias desde el inicio:

1. **Claude API (Anthropic)**
   - Crear cuenta en: https://console.anthropic.com/
   - Obtener API key en: Settings → API Keys
   - Agregar a `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

2. **Replicate API** (para Flux/Ideogram)
   - Crear cuenta en: https://replicate.com/
   - Obtener token en: Account → API tokens
   - Agregar a `.env`: `REPLICATE_API_TOKEN=r8_...`

3. **ElevenLabs API**
   - Crear cuenta en: https://elevenlabs.io/
   - Plan Free: 10,000 caracteres/mes (suficiente para ~10 videos)
   - Obtener API key en: Profile → API Key
   - Agregar a `.env`: `ELEVENLABS_API_KEY=...`

4. **Hedra API**
   - Crear cuenta en: https://www.hedra.com/
   - Plan Free: ~7 videos/mes
   - Obtener API key en: Dashboard → API
   - Agregar a `.env`: `HEDRA_API_KEY=...`

## 🚀 Uso

### Generar un video completo (Fase 1)

#### Paso 1: Generar guion
```bash
python scripts/01_guion.py

# O con tema específico:
python scripts/01_guion.py "El perro quiere salir a pasear pero está lloviendo"
```

Esto generará:
- `assets_temp/guiones/{session_id}_guion.json`

#### Paso 2: Validar guion
```bash
python scripts/02_validador.py {session_id}
```

El validador evalúa 4 criterios:
1. Comedia universal (funciona para 12 años y 35 años)
2. Gatillo de identificación ("así es mi papá/mamá")
3. Lenguaje panlatino (sin localismos)
4. Coherencia del personaje

Si falla, reescribe automáticamente (máx. 2 reintentos).

#### Paso 3-7: Próximamente
Los siguientes scripts están en desarrollo:
- `03_imagenes.py` - Generar personajes, fondo, cutaways
- `04_audio.py` - Generar voces con ElevenLabs
- `05_animacion.py` - Animar personajes con Hedra
- `06_montaje.py` - Composición final con ffmpeg
- `07_subtitulos.py` - Subtítulos karaoke

## 📁 Estructura del proyecto

```
elmamon-pipeline/
├── config/
│   ├── style_bible.json       # Guía de estilo visual fija
│   ├── prompt_guion.txt        # Prompt para generación de guion
│   └── prompt_validador.txt    # Prompt para validación
├── scripts/
│   ├── utils.py                # Utilidades compartidas
│   ├── 01_guion.py             # ✅ LISTO
│   ├── 02_validador.py         # ✅ LISTO
│   ├── 03_imagenes.py          # 🚧 En desarrollo
│   ├── 04_audio.py             # 🚧 En desarrollo
│   ├── 05_animacion.py         # 🚧 En desarrollo
│   ├── 06_montaje.py           # 🚧 En desarrollo
│   └── 07_subtitulos.py        # 🚧 En desarrollo
├── assets_temp/                # Archivos intermedios (se limpia)
├── output/                     # Videos finales
├── logs/                       # Registro de cada corrida
├── .env                        # Credenciales (NO SUBIR A GIT)
└── requirements.txt
```

## 🎨 Estilo visual

- **Mascota**: Diseño cartoon con rasgos exagerados, ojos grandes, expresiones marcadas
- **Humanos**: Línea simple/minimalista con rasgos exagerados (no realista)
- **Cutaways**: Ilustraciones cómicas, sin memes con copyright, sin texto
- **Formato**: Vertical 1080x1920, máx. 30 seg, H.264

Ver `config/style_bible.json` para detalles completos.

## 📈 Roadmap

### ✅ Fase 1 - Validación (ACTUAL)
- Planes gratuitos
- Sin publicación
- ~10 videos de prueba/mes
- Costo: Claude API pago por uso (~$5-10/mes)

### 🔜 Fase 2 - Lanzamiento
- Planes básicos/starter
- Publicación automática (3 videos/semana)
- n8n + Meta Graph API + YouTube Data API

### 🔮 Fase 3 - Escalado
- Planes profesionales
- Publicación diaria (~30 videos/mes)

## 🐛 Debugging

Los logs de cada corrida se guardan en:
- `logs/{session_id}.json` - Log estructurado completo
- Consola con colores para seguimiento en vivo

## 📝 Licencia

Proyecto privado - Todos los derechos reservados

---

**Nota:** Este proyecto está en desarrollo activo. Las etapas 3-7 del pipeline se implementarán progresivamente conforme se valide cada fase.
