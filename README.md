# 🎬 elmamon-pipeline

> Pipeline automatizado para generar videos cortos de comedia familiar con IA

[![Fase](https://img.shields.io/badge/Fase-1%20Validaci%C3%B3n-blue)](CONTEXTO.md)
[![Python](https://img.shields.io/badge/Python-3.14-green)](requirements.txt)
[![Licencia](https://img.shields.io/badge/Licencia-Privado-red)]()

---

## 📖 Descripción

Pipeline modular que genera automáticamente videos cortos (Reels/Shorts) de comedia familiar, donde una mascota antropomorfizada (perro, gato o loro) interactúa con miembros de una familia en situaciones cotidianas.

**Formato:** Humor basado en malentendidos con estilo mexicano o colombiano  
**Duración:** 30 segundos  
**Público:** 10-12 años hasta adultos  
**Objetivo:** Generar identificación ("así es mi papá/mamá", "eso me pasó a mí")

---

## ✨ Características

- ✅ **Generación automática de guiones** con Claude API
- ✅ **Validación de calidad** con 4 criterios (comedia, expresiones, identificación, contraste)
- ✅ **Reescritura automática** si el guion no cumple los criterios
- ✅ **Estructura organizada** por carpetas numeradas (`001-yyyyMMdd/`)
- 🚧 Generación de imágenes con IA (Replicate)
- 🚧 Síntesis de voz (ElevenLabs)
- 🚧 Animación con lip-sync (Hedra)
- 🚧 Montaje automático (ffmpeg)
- ⏸️ Publicación automática en redes (Fase 2)

---

## 🚀 Quick Start

### 1. Requisitos

- Python 3.10+
- ffmpeg
- APIs: Claude, Replicate, ElevenLabs, Hedra

### 2. Instalación

```bash
# Clonar repositorio
git clone https://github.com/guigo0627/elmamon-pipeline.git
cd elmamon-pipeline

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
cp .env.template .env
# Editar .env con tus API keys

# Verificar instalación
python scripts/test_setup.py
```

### 3. Generar tu primer video

```bash
# Generar guion
python scripts/01_guion.py

# Validar guion
python scripts/02_validador.py <session_id>

# O usar el pipeline completo
python pipeline.py --tema "El gato no quiere bañarse"
```

---

## 📂 Estructura del Proyecto

```
elmamon-pipeline/
├── CONTEXTO.md              # Estado del proyecto (leer al inicio de cada sesión)
├── docs/                    # Documentación completa
│   ├── architecture/        # Arquitectura técnica
│   ├── guides/              # Guías de uso
│   ├── specs/               # Especificaciones y estilo
│   └── prompts/             # Prompts de IA versionados
├── scripts/                 # Scripts del pipeline
│   ├── 01_guion.py         # Generación de guion ✅
│   ├── 02_validador.py     # Validación de guion ✅
│   └── utils.py            # Utilidades compartidas
└── output/                  # Videos generados (no en repo)
```

---

## 🎯 Roadmap

### Fase 1 - Validación (Actual)
- [x] Generación de guiones
- [x] Validación automática
- [ ] Generación de imágenes
- [ ] Síntesis de voz
- [ ] Animación con lip-sync
- [ ] Montaje final

**Objetivo:** 10 videos de prueba con planes gratuitos

### Fase 2 - Lanzamiento
- [ ] Publicación automática (n8n + APIs)
- [ ] 3 videos/semana

### Fase 3 - Escalado
- [ ] Publicación diaria
- [ ] Procesamiento en paralelo
- [ ] Cache de assets

---

## 📚 Documentación

- **[CONTEXTO.md](CONTEXTO.md)** - Estado actual del proyecto y próximos pasos
- **[Guía de Inicio Rápido](docs/guides/INICIO_RAPIDO.md)** - Primeros pasos
- **[Configuración](docs/guides/CONFIGURACION_PASO_A_PASO.md)** - Setup detallado
- **[Arquitectura](docs/architecture/ARQUITECTURA.md)** - Diseño técnico
- **[Guiones de Referencia](docs/specs/guiones_referencia.md)** - Ejemplos de humor

---

## 💰 Costos (Fase 1)

| Servicio | Costo |
|----------|-------|
| Claude API | ~$0.75/guion |
| Replicate | ~$0.30/video |
| ElevenLabs | Gratis (plan Free) |
| Hedra | Gratis (plan Free) |
| **Total** | **~$1.50/video** |

**Presupuesto Fase 1:** $15-20 USD para 10 videos de prueba

---

## 🛠️ Tecnologías

- **IA:** Claude API, Replicate (Flux/Ideogram), ElevenLabs, Hedra
- **Lenguaje:** Python 3.14
- **Video:** ffmpeg
- **Procesamiento:** Pillow, rembg, numpy

---

## 📊 Estado Actual

- ✅ **2 guiones aprobados** listos para siguiente etapa
- ✅ Pipeline de generación funcionando
- ✅ Validador optimizado (menos estricto, enfoque en semántica)
- 🚧 Próximo paso: Desarrollar Etapa 2 (generación de imágenes)

---

## 👨‍💻 Autor

**Guillermo Gonzalez**  
📧 guillermo_jose15@hotmail.com

---

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

---

## 🔗 Enlaces Útiles

- [Anthropic Console](https://console.anthropic.com/)
- [Replicate](https://replicate.com/)
- [ElevenLabs](https://elevenlabs.io/)
- [Hedra](https://www.hedra.com/)

---

**Última actualización:** 2026-09-04  
**Versión:** 1.0.0 (Fase 1)
