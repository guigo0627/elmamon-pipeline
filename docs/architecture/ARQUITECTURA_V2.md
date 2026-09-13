# ARQUITECTURA V2 - PIPELINE PROFESIONAL (AUDIO-FIRST)

**Creado:** 2026-09-10  
**Enfoque:** Input = Audio → Output = Video profesional animado  
**Timeline:** 3 días desarrollo

---

## 🎯 FLUJO COMPLETO

```
INPUT: Audio MP3/MPEG (conversación entre personajes)
    ↓
┌─────────────────────────────────────────────────┐
│ FASE 1: TRANSCRIPCIÓN Y ANÁLISIS               │
│ - AssemblyAI: Transcripción + Speaker Diarization │
│ - Identificar género de voces (hombre/mujer)    │
│ - Timestamps palabra por palabra                │
│ - Detección emocional por segmento             │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ AGENTE 1: DIRECTOR DE ANIMACIÓN (Claude)       │
│ - Analiza transcripción + emociones            │
│ - Selecciona personajes según género detectado │
│ - Planifica expresiones por segmento           │
│ - Genera keyframes para gestos                 │
│ - Output: animation_plan.json                  │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ FASE 2: ANIMACIÓN                              │
│ - Manim Community: Rigging de personajes      │
│ - Rhubarb: Lip sync preciso                    │
│ - Gestos programáticos (manos, brazos)        │
│ - Output: escenas_animadas/*.mp4              │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ AGENTE 2: EDITOR DE VIDEO (Claude)             │
│ - Analiza timing y emociones del audio        │
│ - Planifica cortes cada 2-3 segundos          │
│ - Determina momentos para zoom                │
│ - Selecciona memes según contexto             │
│ - Output: edit_timeline.json                  │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ FASE 3: COMPOSICIÓN PROFESIONAL                │
│ - MoviePy: Compositor principal                │
│ - Cortes dinámicos cada 2-3s                   │
│ - Zoom programático                            │
│ - Subtítulos karaoke                           │
│ - Insert de memes en timing preciso            │
│ - Transiciones profesionales                   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ AGENTE 3: INGENIERO DE PIPELINE (Python)       │
│ - Orquesta todo el proceso                     │
│ - Maneja errores y reintentos                  │
│ - Optimiza rendimiento                         │
│ - Cache de resultados intermedios             │
└─────────────────────────────────────────────────┘
    ↓
OUTPUT: video_final.mp4 (1080x1920, 30fps, profesional)
```

---

## 📦 MÓDULOS Y SCRIPTS

### **MÓDULO 1: Transcripción (scripts/pipeline_v2/01_transcribe.py)**
```python
Responsabilidad:
- Subir audio a AssemblyAI
- Obtener transcripción con timestamps
- Speaker diarization (detectar voces A y B)
- Sentiment analysis básico

Input:  assets/input_audios/Audio_prueba.mpeg
Output: output/{video_id}/transcription.json
```

### **MÓDULO 2: Análisis Inteligente (scripts/pipeline_v2/02_analyze.py)**
```python
Responsabilidad:
- AGENTE 1 (Director Animación) analiza transcripción
- Identifica género de speakers (voz grave=hombre, aguda=mujer)
- Mapea emociones por segmento (feliz, enojado, sorprendido, etc)
- Genera plan de animación detallado

Input:  output/{video_id}/transcription.json
Output: output/{video_id}/animation_plan.json
```

### **MÓDULO 3: Generación de Personajes (scripts/pipeline_v2/03_characters.py)**
```python
Responsabilidad:
- Lee animation_plan.json
- Selecciona personajes de assets/personajes_base/
- Genera variaciones si es necesario
- Prepara assets para animación

Input:  output/{video_id}/animation_plan.json
Output: output/{video_id}/characters/
```

### **MÓDULO 4: Animación con Manim (scripts/pipeline_v2/04_animate.py)**
```python
Responsabilidad:
- Crea escenas con Manim Community
- Rigging de personajes stick figure
- Gestos de manos programáticos
- Movimientos corporales según emoción

Input:  output/{video_id}/animation_plan.json
Output: output/{video_id}/animated_scenes/*.mp4
```

### **MÓDULO 5: Lip Sync (scripts/pipeline_v2/05_lipsync.py)**
```python
Responsabilidad:
- Rhubarb procesa audio por segmento
- Genera mouth shapes con timestamps
- Integra con animación de Manim

Input:  output/{video_id}/audio_segments/*.wav
Output: output/{video_id}/lipsync/*.json
```

### **MÓDULO 6: Planificación Editorial (scripts/pipeline_v2/06_edit_plan.py)**
```python
Responsabilidad:
- AGENTE 2 (Editor) analiza audio + transcripción
- Planifica cortes cada 2-3 segundos
- Determina momentos para zoom
- Selecciona memes del banco
- Genera timeline de edición

Input:  output/{video_id}/transcription.json
Output: output/{video_id}/edit_timeline.json
```

### **MÓDULO 7: Composición Final (scripts/pipeline_v2/07_compose.py)**
```python
Responsabilidad:
- AGENTE 3 (Ingeniero) ejecuta plan editorial
- Compositor profesional con MoviePy
- Cortes dinámicos
- Zoom programático
- Subtítulos karaoke
- Insert de memes
- Transiciones

Input:  output/{video_id}/edit_timeline.json
        output/{video_id}/animated_scenes/*.mp4
Output: output/{video_id}/video_final.mp4
```

### **MÓDULO 8: Orquestador (scripts/pipeline_v2/run_pipeline.py)**
```python
Responsabilidad:
- Ejecuta módulos 1-7 en orden
- Maneja errores y logging
- Cache de resultados
- Reintentos inteligentes

Input:  assets/input_audios/*.mpeg
Output: output/{video_id}/video_final.mp4
```

---

## 🔧 TECNOLOGÍAS Y DEPENDENCIAS

### **APIs Externas:**
```python
# Transcripción
assemblyai==0.28.0  # $0.00025/segundo (~$0.0075 por video 30s)

# IA (gratis)
anthropic-sdk  # Para agentes Claude
```

### **Animación:**
```python
# Manim Community (rigging real)
manim==0.18.0  # Gratis, open source

# Lip Sync
# Rhubarb (ya instalado en tools/rhubarb/)
```

### **Video/Audio:**
```python
moviepy==2.2.1      # Compositor principal
opencv-python==4.10.0  # Procesamiento visual
pillow==11.3.0      # Manipulación imágenes
ffmpeg-python==0.2.0  # Conversiones
pydub==0.25.1       # Procesamiento audio
```

### **Utilidades:**
```python
numpy==1.26.4
scipy==1.14.1       # Para análisis de audio
matplotlib==3.9.2   # Visualizaciones
```

---

## 📊 FORMATOS DE DATOS

### **transcription.json:**
```json
{
  "audio_duration": 30.5,
  "speakers": [
    {
      "speaker": "A",
      "gender_detected": "female",  // Inferido por tono
      "segments": [
        {
          "start": 0.0,
          "end": 2.5,
          "text": "Mi mujer disculpándose conmigo:",
          "confidence": 0.95,
          "emotion": "neutral"
        }
      ]
    },
    {
      "speaker": "B",
      "gender_detected": "male",
      "segments": [...]
    }
  ]
}
```

### **animation_plan.json:**
```json
{
  "characters": {
    "speaker_A": {
      "type": "mujer_base",
      "name": "Mujer",
      "position": "left"
    },
    "speaker_B": {
      "type": "hombre_base",
      "name": "Hombre",
      "position": "right"
    }
  },
  "scenes": [
    {
      "start": 0.0,
      "end": 2.5,
      "speaker": "A",
      "text": "Mi mujer disculpándose conmigo:",
      "emotion": "neutral",
      "gestures": ["hands_on_hips"],
      "expression": "base",
      "camera": {"zoom": 1.0, "pan": "center"}
    },
    {
      "start": 2.5,
      "end": 5.0,
      "speaker": "B",
      "text": "...",
      "emotion": "confused",
      "gestures": ["shrug"],
      "expression": "confundido",
      "camera": {"zoom": 1.2, "pan": "right"}
    }
  ]
}
```

### **edit_timeline.json:**
```json
{
  "cuts": [
    {"time": 0.0, "type": "fade_in"},
    {"time": 2.5, "type": "cut", "camera": "speaker_B"},
    {"time": 5.0, "type": "cut", "camera": "wide"},
    {"time": 7.5, "type": "cut", "camera": "speaker_A"}
  ],
  "zooms": [
    {"start": 10.0, "end": 12.0, "from": 1.0, "to": 1.3}
  ],
  "memes": [
    {
      "time": 15.0,
      "duration": 2.0,
      "image": "assets/memes/confused_face.png",
      "position": "top_right",
      "size": 300
    }
  ],
  "subtitles": {
    "style": "karaoke",
    "position": "bottom",
    "font_size": 70,
    "color_default": "#FFFFFF",
    "color_active": "#FFD700"
  }
}
```

---

## 💰 COSTOS ESTIMADOS

### **Por Video (30 segundos):**
- AssemblyAI transcripción: $0.0075
- APIs de Claude (análisis): $0.00 (cache + lote)
- Manim + Rhubarb: $0.00 (local)
- MoviePy: $0.00 (local)

**Total: ~$0.01 USD/video** ✅

### **Para 100 videos:**
- Total: ~$1.00 USD
- Bien dentro del presupuesto de $10 USD

---

## ⏱️ TIEMPOS ESTIMADOS

### **Desarrollo (una vez):**
- Día 1: Transcripción + Análisis (6-8h)
- Día 2: Animación con Manim (8-10h)
- Día 3: Composición profesional (8-10h)
**Total: 3 días desarrollo**

### **Generación por Video (automatizado):**
- Transcripción: 2-3 min
- Análisis IA: 1-2 min
- Animación: 5-10 min (depende duración)
- Composición: 3-5 min
- Renderizado: 2-3 min
**Total: 15-25 minutos por video** ✅

---

## 🎯 CALIDAD OBJETIVO

Basado en las imágenes de referencia del usuario:
- ✅ Personajes stick figure simples pero animados
- ✅ Movimientos de brazos y manos expresivos
- ✅ Lip sync convincente
- ✅ Background real (foto de sala/cocina)
- ✅ Subtítulos profesionales
- ✅ Cortes dinámicos cada 2-3s
- ✅ Sensación profesional como "Ignacio Animados"

**Meta: 80-90% de calidad del referente**

---

## 🚨 RIESGOS Y MITIGACIONES

### **Riesgo 1: Manim difícil de aprender**
**Mitigación:** Templates pre-hechos + sistema programático simple

### **Riesgo 2: Detección de género imprecisa**
**Mitigación:** Permitir override manual en config

### **Riesgo 3: Renderizado lento**
**Mitigación:** Cache agresivo + renderizado por partes

### **Riesgo 4: AssemblyAI límite de rate**
**Mitigación:** Cola de procesamiento + reintentos

---

## 📂 ESTRUCTURA DE CARPETAS

```
elmamon-pipeline/
├── scripts/
│   └── pipeline_v2/          # NUEVO pipeline
│       ├── 01_transcribe.py
│       ├── 02_analyze.py
│       ├── 03_characters.py
│       ├── 04_animate.py
│       ├── 05_lipsync.py
│       ├── 06_edit_plan.py
│       ├── 07_compose.py
│       ├── run_pipeline.py
│       └── agents/
│           ├── animation_director.py
│           ├── video_editor.py
│           └── pipeline_engineer.py
├── assets/
│   ├── input_audios/         # Audios de entrada
│   ├── personajes_base/      # Personajes stick
│   ├── backgrounds/          # Fondos reales
│   └── memes/               # Banco de memes
├── output/
│   └── {video_id}/
│       ├── transcription.json
│       ├── animation_plan.json
│       ├── edit_timeline.json
│       ├── characters/
│       ├── animated_scenes/
│       ├── lipsync/
│       └── video_final.mp4
└── ARQUITECTURA_V2.md       # Este documento
```

---

## ✅ CHECKLIST DE DESARROLLO

### **DÍA 1: Fundamentos**
- [ ] Instalar AssemblyAI SDK
- [ ] Implementar 01_transcribe.py
- [ ] Crear AGENTE 1 (Director Animación)
- [ ] Implementar 02_analyze.py
- [ ] Probar con Audio_prueba.mpeg
- [ ] Validar transcription.json y animation_plan.json

### **DÍA 2: Animación**
- [ ] Instalar Manim Community
- [ ] Crear templates de personajes stick
- [ ] Implementar sistema de gestos
- [ ] Implementar 04_animate.py
- [ ] Integrar 05_lipsync.py con Rhubarb
- [ ] Generar primera animación de prueba

### **DÍA 3: Composición**
- [ ] Crear AGENTE 2 (Editor Video)
- [ ] Implementar 06_edit_plan.py
- [ ] Crear compositor profesional 07_compose.py
- [ ] Sistema de cortes dinámicos
- [ ] Zoom programático
- [ ] Subtítulos karaoke
- [ ] Insert de memes
- [ ] Renderizado final optimizado
- [ ] VIDEO COMPLETO funcionando

---

**Última actualización:** 2026-09-10 21:30  
**Estado:** Arquitectura definida, comenzando implementación  
**Próximo:** Implementar Módulo 1 (Transcripción)
