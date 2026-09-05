# 🎬 CONTEXTO - elmamon-pipeline

> **Archivo de sesión:** Lee este documento al inicio de cada sesión para retomar el proyecto

---

## 📍 Estado Actual

**Fecha última actualización:** 2026-09-04  
**Fase del proyecto:** 1 - Validación (Exploratoria)  
**Sesión actual:** Configuración completada + Primeros guiones generados  
**Líneas de código:** ~2,200  

### ✅ Completado Hoy (2026-09-04)

**Infraestructura:**
- ✅ Estructura modular y escalable del proyecto
- ✅ Sistema de logging con colores (corregido encoding Windows)
- ✅ Gestión de sesiones con timestamps
- ✅ Documentación arquitectónica completa
- ✅ Estructura de output organizada por carpetas numeradas (`###-yyyyMMdd`)

**APIs Configuradas (4/4):**
- ✅ **Claude API** (Anthropic) - $5 USD recargados
- ✅ **Replicate API** - $10 USD recargados
- ✅ **ElevenLabs API** - Acceso Full
- ✅ **Hedra API** - Plan Free

**Pipeline operativo (Etapas 1-1.5):**
- ✅ **Etapa 1:** Generación de guion con Claude API
  - Selección automática de elenco (2-3 personajes)
  - Elección de especie de mascota (perro/gato/loro)
  - Marcado de cutaways en el diálogo
  - Output en JSON estructurado
  - Guarda en carpetas numeradas: `output/###-yyyyMMdd/`
- ✅ **Etapa 1.5:** Validación de guion contra 4 criterios
  - Comedia efectiva (patrón de malentendido)
  - Expresiones locales (México O Colombia, nunca mezclar)
  - Identificación familiar
  - Exageración y contraste
  - Reescritura automática (hasta 2 reintentos)
  - Validador actualizado: menos estricto, enfoque en semántica

**Videos Generados:**
- ✅ **Video 001-20260904:** "¿Dormiste bien?" → Filosofía del sueño (APROBADO)
- ✅ **Video 002-20260904:** "¿Ya comiste?" → Filosofía del comer (APROBADO MANUAL)

**Documentación:**
- ✅ `docs/README.md` - Documentación completa
- ✅ `docs/guides/INICIO_RAPIDO.md` - Quick start
- ✅ `docs/guides/CONFIGURACION_PASO_A_PASO.md` - Guía detallada de configuración
- ✅ `docs/architecture/ARQUITECTURA.md` - Arquitectura técnica
- ✅ `docs/specs/` - Especificaciones, style bible, guiones de referencia
- ✅ `docs/prompts/` - Prompts de IA versionados y optimizados

### 🚧 En Desarrollo (Próximos pasos)

1. **Etapa 2: Generación de imágenes** (`scripts/03_imagenes.py`)
   - Integración con Replicate API (Flux/Ideogram)
   - Generación de personajes según style bible
   - Generación de fondo según escenario
   - Generación de cutaways
   - Remoción de fondo con rembg

2. **Etapa 3-7:** Audio, animación, montaje, subtítulos

---

## 📂 Estructura del Proyecto

```
elmamon-pipeline/
├── CONTEXTO.md                    ← ESTE ARCHIVO (estado del proyecto)
├── .env                           ← Credenciales (NO subir a git)
├── .env.template                  ← Plantilla de configuración
├── requirements.txt               ← Dependencias Python
├── pipeline.py                    ← Orquestador principal
│
├── docs/                          ← Documentación centralizada
│   ├── README.md                  ← Documentación completa
│   ├── architecture/
│   │   └── ARQUITECTURA.md        ← Arquitectura técnica
│   ├── guides/
│   │   ├── INICIO_RAPIDO.md       ← Quick start
│   │   └── CONFIGURACION_PASO_A_PASO.md
│   ├── specs/
│   │   ├── requerimientos-originales.md
│   │   ├── style_bible.json       ← Guía de estilo visual
│   │   └── guiones_referencia.md  ← Ejemplos de guiones
│   └── prompts/                   ← Prompts versionados
│       ├── prompt_guion.txt       ← Generación de guion
│       └── prompt_validador.txt   ← Validación de guion
│
├── scripts/                       ← Pipeline scripts
│   ├── utils.py                   ← Utilidades compartidas
│   ├── 01_guion.py               ← ✅ Generación de guion
│   ├── 02_validador.py           ← ✅ Validación de guion
│   ├── 03_imagenes.py            ← 🚧 TODO
│   ├── 04_audio.py               ← 🚧 TODO
│   ├── 05_animacion.py           ← 🚧 TODO
│   ├── 06_montaje.py             ← 🚧 TODO
│   ├── 07_subtitulos.py          ← 🚧 TODO
│   ├── 08_publicacion.py         ← ⏸️ Fase 2+
│   └── test_setup.py             ← Verificador de configuración
│
├── output/                        ← Videos finales organizados
│   ├── 001-20260904/              ← Video #1 (APROBADO)
│   │   ├── guion.json
│   │   ├── APROBADO.txt
│   │   ├── validacion_intento*.json
│   │   ├── personajes/
│   │   ├── audio/
│   │   ├── animaciones/
│   │   └── cutaways/
│   └── 002-20260904/              ← Video #2 (APROBADO MANUAL)
│       └── ...
│
├── assets_temp/                   ← Temporales (ignorados en git)
├── logs/                          ← Logs por sesión (ignorados en git)
└── temp/                          ← Temporales (ignorados en git)
```

---

## 🎯 Roadmap

### Fase 1 - Validación (ACTUAL)
**Objetivo:** Generar 10 videos de prueba con planes gratuitos para validar calidad.

**Estado actual:**
- ✅ Etapas 1-1.5: Guion + Validación (COMPLETADAS)
- ✅ 2 videos con guiones aprobados
- 🚧 Etapas 2-7: Generación completa del video (PENDIENTE)
- ⏸️ Etapa 8: Publicación (Pospuesto a Fase 2)

**Límites de Fase 1:**
- ElevenLabs Full: Suficiente para fase 1
- Hedra Free: ~7 videos/mes → **LIMITANTE PRINCIPAL**
- Costo por video: ~$1.50 USD (guion + validación + imágenes)
- Presupuesto Fase 1: $15-20 USD restantes

### Fase 2 - Lanzamiento
**Objetivo:** Publicación automática, 3 videos/semana.

**Cambios:**
- Planes básicos de APIs (Hedra Basic)
- Activar Etapa 8: Publicación con n8n
- Integración con Meta Graph API + YouTube Data API
- Costo estimado: ~$40-50/mes

### Fase 3 - Escalado
**Objetivo:** Publicación diaria, ~30 videos/mes.

**Cambios:**
- Planes profesionales de APIs
- Procesamiento en paralelo
- Cache de assets recurrentes
- Queue system (Redis/Celery)
- Costo estimado: ~$150-200/mes

---

## 🚀 Próximos Pasos Inmediatos

### 1. Desarrollar Etapa 2: Generación de Imágenes 🎨

**Archivo:** `scripts/03_imagenes.py`

**Tareas:**
- [ ] Integrar Replicate API
- [ ] Cargar style_bible.json
- [ ] Generar personajes (mascota + humanos)
- [ ] Generar fondo según escenario
- [ ] Generar cutaways según marcas en el guion
- [ ] Remoción de fondo con rembg
- [ ] Guardar en `output/###-yyyyMMdd/personajes/`

**Probar con:** Video 001-20260904

### 2. Documentar aprendizajes

**Lecciones de hoy:**
- El validador debe ser estricto en lo importante (no mezclar países) pero flexible en detalles
- La estructura de carpetas numeradas facilita enormemente la organización
- Los guiones requieren 1-2 reintentos en promedio para aprobarse
- Costo real por guion aprobado: ~$0.75-1.00 USD

---

## 💰 Inversión y Costos

### Inversión inicial realizada:
- Claude API: $5 USD
- Replicate API: $10 USD
- ElevenLabs: Acceso Full
- Hedra: Plan Free
- **Total:** $15 USD

### Costos de hoy:
- Generación de 2 guiones: ~$1.00 USD
- Validaciones (6 intentos): ~$1.50 USD
- **Total gastado hoy:** ~$2.50 USD

### Presupuesto restante:
- Claude + Replicate: ~$12.50 USD
- Suficiente para: 8-10 videos más con guion + imágenes

---

## 📊 Métricas de Éxito (Fase 1)

### Objetivo principal
✅ Generar 10 videos completos que cumplan:
1. ✅ Guion aprobado (4 criterios) → **2/10 logrados**
2. 🚧 Calidad visual (personajes + animación reconocibles)
3. 🚧 Audio claro y cómico
4. 🚧 Duración ≤30 segundos
5. 🚧 Formato vertical 1080x1920

### Criterio de aprobación de Fase 1
- Al menos 7/10 videos cumplen todos los criterios
- Feedback positivo de 3+ personas del público objetivo (12-35 años)
- Costo real ≤ $20/mes

**Si se aprueba Fase 1 → Escalar a Fase 2**

---

## 🐛 Debugging

### Logs por sesión
```bash
# Ver último log
ls -lt logs/ | head -2

# Ver log específico
cat logs/20260904_*.json | py -m json.tool
```

### Ver guiones generados
```bash
# Listar videos
ls -la output/

# Ver guion de un video
cat output/001-20260904/guion.json | py -m json.tool
```

### Limpiar temporales
```bash
# Limpiar assets temporales
rm -rf assets_temp/*

# Limpiar carpeta temp
rm -rf temp/*
```

---

## 📚 Recursos Importantes

### Documentación
- **Arquitectura completa:** `docs/architecture/ARQUITECTURA.md`
- **Guía de inicio:** `docs/guides/INICIO_RAPIDO.md`
- **Configuración paso a paso:** `docs/guides/CONFIGURACION_PASO_A_PASO.md`
- **Especificaciones:** `docs/specs/`
- **README principal:** `docs/README.md`

### APIs Configuradas
1. **Claude API:** https://console.anthropic.com/
2. **Replicate API:** https://replicate.com/
3. **ElevenLabs API:** https://elevenlabs.io/
4. **Hedra API:** https://www.hedra.com/

### Herramientas
- **ffmpeg:** Para montaje y subtítulos (instalado)
- **rembg:** Para remoción de fondo (instalado)

---

## ✅ Checklist de Sesión

Al iniciar una sesión:
- [ ] Leer este CONTEXTO.md completo
- [ ] Revisar última fecha de actualización
- [ ] Verificar fase actual del proyecto
- [ ] Revisar "Próximos pasos inmediatos"
- [ ] Revisar últimos logs si hubo trabajo previo

Al terminar una sesión:
- [x] Actualizar sección "Estado Actual"
- [x] Actualizar "Próximos pasos inmediatos"
- [x] Documentar decisiones importantes
- [x] Commitear cambios si hay progreso significativo

---

## 🎓 Aprendizajes y Decisiones

### Decisiones de diseño
1. **Modularidad estricta:** Cada etapa es independiente y testeable
2. **Estado persistente:** Todos los outputs se guardan para debugging
3. **Configuración externalizada:** Prompts y specs fuera del código
4. **Escalabilidad desde diseño:** Preparado para Fase 2 y 3 sin refactoring
5. **Documentación centralizada:** Todo en docs/, solo CONTEXTO.md en raíz
6. **Output organizado:** Carpetas numeradas `###-yyyyMMdd` por cada video

### Lecciones aprendidas (2026-09-04)
1. **Validador flexible:** Debe ser estricto en lo importante (no mezclar países) pero flexible en detalles menores
2. **Consistencia de país:** NUNCA mezclar expresiones mexicanas y colombianas en el mismo guion
3. **Estructura numerada:** Las carpetas `001-yyyyMMdd` facilitan tracking y organización
4. **Reintentos son normales:** Los guiones requieren 1-2 reintentos en promedio
5. **Costo real:** ~$0.75-1.00 USD por guion aprobado (incluyendo reintentos)
6. **Encoding Windows:** Necesario configurar UTF-8 explícitamente en scripts

### Prompts optimizados
- **Generador:** Debe elegir México O Colombia al inicio, mínimo 3 expresiones del mismo país
- **Validador:** Flexible en detalles, estricto en no mezclar países y en estructura básica

---

## 🔐 Seguridad

- ✅ `.env` en `.gitignore` (credenciales nunca se suben)
- ✅ `.env.template` con valores de ejemplo
- ✅ Validación de API keys en tiempo de ejecución
- ✅ `assets_temp/`, `logs/`, `temp/` en `.gitignore`
- ✅ Workspace ID configurado para Claude API

---

**Última sesión:** 2026-09-04 (23:30)  
**Duración:** ~4 horas  
**Progreso:** Configuración completa + 2 guiones aprobados  
**Próxima sesión:** Desarrollar Etapa 2 (generación de imágenes)  
**Bloqueadores actuales:** Ninguno  
**Inversión total:** $15 USD inicial + $2.50 USD hoy = $17.50 USD
