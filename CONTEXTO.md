# CONTEXTO DEL PROYECTO - Pipeline de Videos Animados

**Última actualización:** 2026-09-10  
**Versión:** 2.0 (Reset completo - Audio-First)

---

## 🎯 OBJETIVO DEL PROYECTO

Pipeline 100% automatizado para generar videos tipo "Ignacio Animados" para YouTube Shorts y Facebook Reels:

**INPUT:** Audio MP3/MPEG (conversación entre personajes)  
**OUTPUT:** Video profesional animado (1080x1920, 30fps)

### **Características del video objetivo:**
- ✅ Personajes stick figure animados con rigging real
- ✅ Movimientos de brazos, manos y cuerpo expresivos
- ✅ Lip sync preciso sincronizado con audio
- ✅ Background real (sala, cocina, etc)
- ✅ Subtítulos tipo karaoke (amarillo progresivo)
- ✅ Cortes dinámicos cada 2-3 segundos
- ✅ Zoom programático en momentos clave
- ✅ Insert de memes según contexto
- ✅ Composición profesional

---

## 📊 ESTADO ACTUAL

### **✅ DECISIONES TOMADAS:**
1. **Reset completo del enfoque** (2026-09-10)
2. **Input = Audio** (no más generación de guiones)
3. **Arquitectura de 3 agentes especializados**
4. **Timeline: 3 días desarrollo**

### **❌ ENFOQUE ANTERIOR (DESCARTADO):**
- Generación de guiones con Claude ❌
- Generación de audio con ElevenLabs ❌
- Personajes estáticos con bocas dibujadas ❌
- Meta Animated Drawings (nunca funcionó) ❌
- Composición simple sin cortes dinámicos ❌

**Razón del reset:** Una semana de trabajo sin resultados cercanos al objetivo

---

## 🏗️ ARQUITECTURA V2 (AUDIO-FIRST)

### **FLUJO COMPLETO:**

```
INPUT: Audio (conversación 2 personas)
    ↓
1. TRANSCRIPCIÓN
   - AssemblyAI: Transcripción + Speaker Diarization
   - Identificar voces A y B
   - Timestamps palabra por palabra
   - Análisis emocional
    ↓
2. AGENTE 1: Director de Animación (Claude)
   - Identifica género de speakers
   - Selecciona personajes
   - Planifica expresiones por segmento
   - Genera keyframes para gestos
    ↓
3. ANIMACIÓN
   - Manim Community: Rigging de personajes
   - Rhubarb: Lip sync preciso
   - Gestos programáticos (manos, brazos)
    ↓
4. AGENTE 2: Editor de Video (Claude)
   - Planifica cortes cada 2-3s
   - Determina momentos para zoom
   - Selecciona memes según contexto
    ↓
5. COMPOSICIÓN PROFESIONAL
   - MoviePy: Compositor principal
   - Cortes dinámicos
   - Zoom programático
   - Subtítulos karaoke
   - Insert de memes
    ↓
OUTPUT: video_final.mp4 (profesional)
```

---

## 💰 PRESUPUESTO Y COSTOS

### **Inversión inicial:** $10 USD (crédito Replicate)
### **Gastado hasta ahora:** ~$0.40 USD (pruebas Flux)
### **Disponible:** ~$9.60 USD

### **Costo por video (estimado):**
- AssemblyAI transcripción: $0.0075 (30s de audio)
- Manim + Rhubarb: $0.00 (gratis, local)
- MoviePy: $0.00 (gratis, local)

**Total: ~$0.01 USD/video** ✅  
**Capacidad: ~900 videos con presupuesto restante**

---

## 🛠️ TECNOLOGÍAS CLAVE

### **APIs Externas:**
- **AssemblyAI:** Transcripción + Speaker Diarization
- **Anthropic Claude:** Agentes inteligentes (análisis, planificación)

### **Librerías Python:**
- **Manim Community:** Animación programática con rigging
- **MoviePy:** Compositor de video profesional
- **Rhubarb Lip Sync:** Sincronización labial
- **OpenCV:** Procesamiento de imágenes
- **Pillow:** Manipulación de assets

---

## 📁 ESTRUCTURA DEL PROYECTO

```
elmamon-pipeline/
├── assets/
│   ├── input_audios/         # 🎵 Audios de entrada
│   ├── personajes_base/      # 🎭 Personajes stick figure
│   ├── backgrounds/          # 🖼️ Fondos reales
│   └── memes/               # 😂 Banco de memes
│
├── scripts/
│   ├── pipeline_v2/         # 🚀 NUEVO pipeline
│   │   ├── 01_transcribe.py
│   │   ├── 02_analyze.py
│   │   ├── 03_characters.py
│   │   ├── 04_animate.py
│   │   ├── 05_lipsync.py
│   │   ├── 06_edit_plan.py
│   │   ├── 07_compose.py
│   │   ├── run_pipeline.py
│   │   └── agents/
│   │       ├── animation_director.py
│   │       ├── video_editor.py
│   │       └── pipeline_engineer.py
│   │
│   └── [scripts antiguos archivados]
│
├── output/
│   └── ###-yyyyMMdd/           # Ejemplo: 001-20260910
│       ├── transcription.json  # Transcripción con speakers
│       ├── animation_plan.json # Plan de animación (AGENTE 1)
│       ├── edit_timeline.json  # Timeline de edición (AGENTE 2)
│       ├── animated_scenes/    # Escenas animadas
│       ├── audio/             # Archivos de audio originales
│       └── video_final.mp4    # Video renderizado final
│
├── tools/
│   └── rhubarb/             # Lip sync (mantener)
│
├── docs/
│   ├── archive/             # Documentación histórica
│   ├── specs/              # Especificaciones
│   └── architecture/       # Diagramas y arquitectura
│
├── CONTEXTO.md             # 📋 Este archivo (único source of truth)
└── README.md              # Instrucciones básicas
```

---

## 📋 PLAN DE DESARROLLO (3 DÍAS)

### **DÍA 1: FUNDAMENTOS**
**Objetivo:** Transcripción y análisis inteligente funcionando

- [x] Reorganizar proyecto y limpiar archivos antiguos
- [ ] Instalar AssemblyAI SDK
- [ ] Implementar módulo de transcripción
- [ ] Crear AGENTE 1 (Director de Animación)
- [ ] Probar con Audio_prueba.mpeg
- [ ] Validar output: transcription.json + animation_plan.json

**Resultado esperado:** Sistema detecta voces, identifica género, genera plan de animación

---

### **DÍA 2: ANIMACIÓN REAL**
**Objetivo:** Personajes animados con gestos y lip sync

- [ ] Instalar Manim Community
- [ ] Crear templates de personajes stick figure
- [ ] Sistema de gestos programáticos
- [ ] Integrar Rhubarb para lip sync
- [ ] Generar primera escena animada

**Resultado esperado:** Video corto con personaje animado + lip sync funcional

---

### **DÍA 3: COMPOSICIÓN PROFESIONAL**
**Objetivo:** Video completo con edición dinámica

- [ ] Crear AGENTE 2 (Editor de Video)
- [ ] Sistema de cortes dinámicos
- [ ] Zoom programático
- [ ] Subtítulos karaoke
- [ ] Insert automático de memes
- [ ] Renderizado final optimizado

**Resultado esperado:** VIDEO COMPLETO de calidad profesional (80-90% del referente)

---

## 🎯 REFERENCIAS Y OBJETIVOS

### **Videos de referencia:**
1. "Ignacio Animados" (TikTok/Instagram)
   - Personajes stick simples pero muy expresivos
   - Animación fluida de brazos y manos
   - Background real (sala con sofá)
   - Subtítulos profesionales

2. Video ejemplo compartido por usuario:
   - Dos personajes conversando
   - Gestos corporales según emoción
   - Composición dinámica

**Meta de calidad:** 80-90% del referente con pipeline automatizado

---

## 🎭 PERSONAJES DISPONIBLES

### **Familia:**
- mamá / mujer
- papá / hombre
- hijo_mayor
- hijo_menor
- hija

### **Círculo social:**
- amigo
- mejor_amigo
- compa
- vecino

**Detección automática:** Sistema identifica género por análisis de voz y selecciona personaje apropiado

---

## ⚙️ CONFIGURACIÓN

### **Variables de entorno (.env):**
```env
ASSEMBLYAI_API_KEY=tu_key_aqui
ANTHROPIC_API_KEY=tu_key_aqui
```

### **Especificaciones de video:**
- Resolución: 1080x1920 (9:16 vertical)
- FPS: 30
- Codec: H.264
- Audio: AAC 128kbps
- Formato: MP4

---

## 📝 APRENDIZAJES CLAVE

### **❌ Lo que NO funcionó (V1):**
1. Meta Animated Drawings - No compatible con Python 3.14
2. Flux para variaciones de personajes - Cambia todo el estilo
3. Personajes estáticos con bocas dibujadas - No se ve profesional
4. Composición simple - Muy aburrida, no engancha
5. Pipeline guion → audio - Muy complejo e innecesario

### **✅ Lo que SÍ funciona (V2):**
1. Input = Audio directo
2. Transcripción automática con AssemblyAI
3. Agentes especializados para planificación
4. Manim para animación programática
5. Composición dinámica con cortes frecuentes

---

## 🚨 RESTRICCIONES CRÍTICAS

1. **$0 inversión adicional** (trabajar con $9.60 restantes)
2. **0 intervención manual por video** (después de setup)
3. **Pipeline 100% automatizado**
4. **Generación en minutos, no horas** (15-25 min/video)
5. **Calidad profesional** (80-90% del referente)

---

## 📊 MÉTRICAS DE ÉXITO

### **Calidad:**
- [ ] Personajes animados con gestos expresivos
- [ ] Lip sync preciso y convincente
- [ ] Cortes dinámicos cada 2-3s
- [ ] Subtítulos karaoke funcionando
- [ ] Video enganchante (no aburrido)

### **Técnico:**
- [ ] Tiempo generación: <30 min/video
- [ ] Costo: <$0.02/video
- [ ] Sin intervención manual
- [ ] Reproducible con cualquier audio

### **Negocio:**
- [ ] Primer video completo en 3 días
- [ ] Pipeline funcional para 10+ videos
- [ ] Dentro del presupuesto de $10 USD

---

## 🔗 RECURSOS

### **Documentación técnica:**
- Ver `docs/architecture/` para diagramas
- Ver `docs/specs/` para especificaciones detalladas

### **APIs:**
- AssemblyAI Docs: https://www.assemblyai.com/docs
- Manim Community: https://docs.manim.community
- Rhubarb Lip Sync: https://github.com/DanielSWolf/rhubarb-lip-sync

---

## 🎬 SIGUIENTE PASO

**AHORA:** Implementar módulo de transcripción (01_transcribe.py)  
**LUEGO:** Crear AGENTE 1 y probar con audio real  
**META:** Primer video completo en 3 días

---

**Estado:** En desarrollo activo (Día 1)  
**Bloqueadores:** Ninguno  
**Energía del equipo:** 🔥 Alta - enfoque correcto esta vez
