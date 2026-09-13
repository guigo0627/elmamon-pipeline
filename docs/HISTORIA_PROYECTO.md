# Historia del Proyecto elmamon-pipeline

## 📅 Cronología de Desarrollo

### Día 1-2: Fundamentos (Sep 4-7, 2026)
**Objetivo:** Crear pipeline base para generación de guiones y validación

**Logros:**
- ✅ Módulo 01: Generador de guiones con Claude API
- ✅ Módulo 02: Validador de calidad (4 criterios)
- ✅ Configuración de APIs: Claude, ElevenLabs, Replicate, Hedra
- ✅ Sistema de logging estructurado
- ✅ Definición de estilo visual (style_bible.json)

**Arquitectura inicial:**
```
Guion → Validador → Imágenes → Audio → Animación → Montaje → Subtítulos
```

### Día 3-7: Módulos de Generación (Sep 7-9, 2026)
**Objetivo:** Implementar generación de imágenes y análisis de contenido

**Logros:**
- ✅ Módulo 03: Generación de personajes base con Replicate (Flux)
- ✅ Análisis de backgrounds con IA (detección de escenarios apropiados)
- ✅ Sistema de análisis de guiones para planning visual
- ✅ Integración con AssemblyAI para transcripción

### Día 8-10: Pivot a Animación 2D (Sep 9-10, 2026)
**DECISIÓN CRÍTICA:** Cambio de estrategia de generación

**Problema detectado:**
- Hedra (animación de fotos) requiere LICENCIA para uso comercial
- Costos altos y restricciones de copyright

**Nueva estrategia:**
- ❌ Generación de imágenes con Flux/Ideogram
- ❌ Animación con Hedra
- ✅ **Personajes stick figure animados con PIL/Python**
- ✅ **Lip sync con Rhubarb Lip Sync**
- ✅ **Backgrounds reales de Pexels/Pixabay (libre de derechos)**

**Ventajas:**
1. **100% libre de copyright** - todo generado o CC0
2. **Zero costos** de imagen/animación
3. **Control total** sobre personajes y expresiones
4. **Escalable** - sin límites de API

### Día 10-12: Pipeline V2 Completo (Sep 10-12, 2026)
**Objetivo:** Primer video completo funcionando

**Módulos implementados:**

#### Pipeline V2 Architecture:
```
01_script_generator.py    → Genera guion + análisis de personajes
02_assemblyai_transcription.py → Transcripción con word-level timestamps
03_character_animator.py  → Personajes animados (PIL)
04_background_downloader.py → Descarga backgrounds CC0
05_tts_generator.py       → Audio con ElevenLabs
06_lip_sync.py            → Mouth cues con Rhubarb
07_video_generator.py     → Genera frames + compone video
08_add_subtitles.py       → Subtítulos karaoke (ASS format)
09_add_static_title.py    → Título estático gancho
```

**Tecnologías clave:**
- **Rhubarb Lip Sync**: Análisis de audio → mouth shapes (A-H, X)
- **MoviePy 2.x**: Composición de video
- **PIL/Pillow**: Dibujo de personajes frame-by-frame
- **ffmpeg**: Procesamiento de video/audio
- **AssemblyAI**: Transcripción con timestamps precisos

**Primer video generado:**
- ✅ 10.88 segundos, 326 frames @ 30 FPS
- ✅ Lip sync sincronizado
- ✅ 2 personajes animados (esposa + esposo)
- ✅ Background real (sala de casa)
- ✅ Audio limpio

### Día 12: Mejoras para Publicación (Sep 12, 2026)
**Objetivo:** Video publication-ready

**5 Mejoras solicitadas:**

1. **Personajes menos "palito"** 🔄
   - Cuerpo con volumen (torso rectangular)
   - Piernas con grosor
   - Pies grandes y con forma
   - Brazos con volumen

2. **Personajes más cerca** ✅
   - X positions: 0.25→0.35 y 0.75→0.65
   - Sensación de conversación

3. **Mejor detección de piso** ✅
   - Sistema de metadata JSON por background
   - Floor position: 87.5% → 90%
   - Evita que personajes queden sobre objetos

4. **Gestos expresivos** 🔄
   - Sistema de expresiones faciales
   - Movimientos de cabeza
   - Gestos corporales (agarrarse cabeza, brazos arriba)

5. **Título estático gancho** ✅
   - Cambio de estrategia: palabra-por-palabra → título fijo
   - Generado por IA: "Cuando mi esposa me pide perdón..."
   - Posicionado al 15% desde arriba

**Estado actual:** 3 de 5 completados

## 🎯 Decisiones de Diseño Importantes

### ¿Por qué stick figures?
1. **Zero copyright issues** - 100% propio
2. **Rápida iteración** - generar frames en segundos
3. **Expresividad** - suficiente para comedia
4. **Escalable** - sin costos por frame

### ¿Por qué NO Hedra/Flux?
1. **Licencias comerciales** caras
2. **Límites de API** restrictivos
3. **Dependencia externa** riesgosa
4. **Copyright incierto** en imágenes generadas

### ¿Por qué Rhubarb Lip Sync?
1. **Open source** y gratuito
2. **Preciso** - análisis fonético real
3. **Rápido** - procesa en < 1 segundo
4. **Comprobado** - usado en juegos indie

## 📊 Métricas Actuales

**Capacidad de generación:**
- Tiempo por video: ~2 minutos (10s de video)
- Frames generados: ~30 FPS
- Calidad: 1080x1920 (9:16)
- Formato: MP4, H.264, AAC

**Costos:**
- Claude API: ~$0.05 por guion
- AssemblyAI: ~$0.025 por minuto de audio
- ElevenLabs: Gratis hasta 10K caracteres/mes
- Total: **~$0.10 por video**

## 🔮 Próximos Pasos

1. **Completar mejoras de personajes** (Punto 1 y 4)
2. **Generar video final** con nuevo audio
3. **Publicar primer video** en YouTube Shorts
4. **Iterar diseño** basado en feedback
5. **Automatizar pipeline completo** (maestro)

## 📚 Lecciones Aprendidas

1. **Simplicidad > Complejidad**: Stick figures funcionan mejor que IA generativa
2. **Control > Dependencia**: Código propio > APIs externas
3. **Iteración rápida**: Poder generar y ver resultados en minutos es clave
4. **MoviePy 2.x**: API diferente (subclipped, with_audio, imports directos)
5. **Windows paths**: Escapar correctamente en ffmpeg (múltiples backslashes)
6. **Python imports**: Archivos con números requieren importlib
7. **Metadata > Detección**: JSON explícito mejor que IA detectando pisos

---

**Última actualización:** 2026-09-12
**Estado del proyecto:** 🟡 En desarrollo activo
**Próximo hito:** Primer video publicable
