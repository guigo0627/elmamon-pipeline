# 🚀 Configuración Paso a Paso - De cero a tu primer video

Esta guía te llevará desde la configuración inicial hasta generar tu primer video completo en Fase 1.

---

## 📋 Pre-requisitos

Antes de empezar, asegúrate de tener:

- [x] **Python 3.10+** instalado
- [x] **Git** instalado (para clonar el proyecto)
- [x] **ffmpeg** instalado (necesario para video)
- [x] **Conexión a Internet** estable
- [x] **Tarjeta de crédito/débito** para APIs pagas (Claude, Replicate)
- [x] **Email válido** para crear cuentas de APIs

---

## Paso 1: Instalar ffmpeg ⚙️

### Windows

**Opción A: Con winget (recomendado)**
```bash
winget install ffmpeg
```

**Opción B: Manual**
1. Ir a https://ffmpeg.org/download.html
2. Descargar Windows build
3. Extraer a `C:\ffmpeg`
4. Agregar a PATH: `C:\ffmpeg\bin`

**Verificar instalación:**
```bash
ffmpeg -version
```

Deberías ver algo como: `ffmpeg version 6.0...`

---

## Paso 2: Instalar dependencias Python 📦

```bash
# Navegar al proyecto
cd c:\Users\ggonzalez38\Downloads\Documentos\Proyecto\channel\elmamon-pipeline

# Instalar dependencias
pip install -r requirements.txt
```

**Tiempo estimado:** 2-3 minutos

**Verificar instalación:**
```bash
python -c "import anthropic, replicate, elevenlabs; print('✅ Dependencias OK')"
```

---

## Paso 3: Configurar API Keys 🔑

### 3.1. Claude API (Anthropic) - **OBLIGATORIA**

**Propósito:** Generar y validar guiones

1. **Crear cuenta:**
   - Ir a: https://console.anthropic.com/
   - Sign up con tu email
   - Verificar email

2. **Obtener API key:**
   - Ir a: https://console.anthropic.com/settings/keys
   - Click en "Create Key"
   - Copiar la key (empieza con `sk-ant-api03-...`)
   - ⚠️ **IMPORTANTE:** Guárdala, solo se muestra una vez

3. **Agregar créditos:**
   - Ir a: https://console.anthropic.com/settings/billing
   - Add credits: $5 USD (suficiente para ~20-30 guiones)

**Costo estimado:** $5 USD para empezar (dura ~1 mes en Fase 1)

---

### 3.2. Replicate API - **OBLIGATORIA**

**Propósito:** Generar imágenes (personajes, fondos, cutaways)

1. **Crear cuenta:**
   - Ir a: https://replicate.com/
   - Sign up con GitHub o email

2. **Obtener API token:**
   - Ir a: https://replicate.com/account/api-tokens
   - Click en "Create token"
   - Copiar el token (empieza con `r8_...`)

3. **Agregar créditos:**
   - Ir a: https://replicate.com/account/billing
   - Add credits: $5 USD (suficiente para ~50-100 imágenes)

**Costo estimado:** $5 USD para empezar (dura ~1 mes en Fase 1)

---

### 3.3. ElevenLabs API - **OBLIGATORIA**

**Propósito:** Generar voces para los personajes

1. **Crear cuenta:**
   - Ir a: https://elevenlabs.io/
   - Sign up (plan Free: 10,000 caracteres/mes)

2. **Obtener API key:**
   - Ir a: https://elevenlabs.io/app/settings/api-keys
   - Click en "Generate new API key"
   - Copiar la key

3. **Plan Free:**
   - ✅ 10,000 caracteres/mes (suficiente para ~10 videos)
   - ✅ Sin tarjeta de crédito necesaria

**Costo estimado:** $0 USD en Fase 1 (plan Free)

---

### 3.4. Hedra API - **OBLIGATORIA**

**Propósito:** Animar personajes con lip-sync

1. **Crear cuenta:**
   - Ir a: https://www.hedra.com/
   - Sign up

2. **Obtener API key:**
   - Ir al Dashboard
   - Sección "API"
   - Copiar la API key

3. **Plan Free:**
   - ✅ ~7 videos/mes
   - ✅ Sin tarjeta de crédito necesaria

**Costo estimado:** $0 USD en Fase 1 (plan Free)

---

### 3.5. Configurar .env

1. **Copiar plantilla:**
```bash
cp .env.template .env
```

2. **Editar .env con tus keys:**

Abrir `.env` en un editor de texto y reemplazar los valores:

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXX

# Replicate
REPLICATE_API_TOKEN=r8_XXXXXXXXXXXXXXXXX

# ElevenLabs
ELEVENLABS_API_KEY=XXXXXXXXXXXXXXXXX

# Hedra
HEDRA_API_KEY=XXXXXXXXXXXXXXXXX

# Configuración
FASE_ACTUAL=1
MAX_DURACION_SEGUNDOS=30
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
```

3. **Guardar el archivo**

⚠️ **IMPORTANTE:** Nunca compartas tu `.env` ni lo subas a git. Ya está en `.gitignore`.

---

## Paso 4: Verificar configuración ✅

Ejecuta el script de verificación:

```bash
python scripts/test_setup.py
```

**Output esperado:**

```
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
VERIFICACIÓN DE CONFIGURACIÓN - elmamon-pipeline
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍

============================================================
1️⃣  VERIFICANDO API KEYS
============================================================
✅ Claude API: Configurada
✅ Replicate (Flux/Ideogram): Configurada
✅ ElevenLabs: Configurada
✅ Hedra: Configurada

============================================================
2️⃣  VERIFICANDO FFMPEG
============================================================
✅ ffmpeg instalado: ffmpeg version 6.0...

============================================================
3️⃣  VERIFICANDO ESTRUCTURA DE CARPETAS
============================================================
✅ docs/
✅ scripts/
✅ assets_temp/
✅ output/
✅ logs/

============================================================
4️⃣  VERIFICANDO DEPENDENCIAS PYTHON
============================================================
✅ anthropic
✅ requests
✅ replicate
✅ elevenlabs
✅ dotenv
✅ PIL
✅ colorlog

============================================================
5️⃣  VERIFICANDO ARCHIVOS DE CONFIGURACIÓN
============================================================
✅ docs/specs/style_bible.json: Guía de estilo visual
✅ docs/prompts/prompt_guion.txt: Prompt de guion
✅ docs/prompts/prompt_validador.txt: Prompt de validador
✅ .env: Credenciales (copiar de .env.template)

============================================================
📊 RESUMEN
============================================================
✅ API Keys
✅ ffmpeg
✅ Directorios
✅ Dependencias
✅ Config Files

============================================================
✅ ¡TODO LISTO! Puedes empezar a generar videos.

Próximo paso:
  python scripts/01_guion.py
============================================================
```

Si ves algún ❌, revisa el paso correspondiente arriba.

---

## Paso 5: Generar tu primer guion 📝

### Opción A: Guion aleatorio

```bash
python scripts/01_guion.py
```

### Opción B: Guion con tema específico

```bash
python scripts/01_guion.py "El perro no quiere bañarse"
```

**Output esperado:**

```
INFO     [01_guion] Iniciando generación de guion para sesión 20260904_214530
INFO     [01_guion] Llamando a Claude API para generar guion...
INFO     [01_guion] ✓ Guion generado exitosamente: assets_temp/guiones/20260904_214530_guion.json
INFO     [01_guion]   - Personajes: 3
INFO     [01_guion]   - Líneas de diálogo: 4
INFO     [01_guion]   - Escenario: sala
INFO     [01_guion]   - Duración estimada: 27 seg

==================================================
GUION GENERADO EXITOSAMENTE
==================================================

Sesión: 20260904_214530
Personajes: mascota, papá, hijo
Escenario: sala

Diálogo:
  1. papá: ¿Por qué el perro no quiere bañarse?
  2. hijo: Porque dice que ya se bañó... el año pasado
  3. mascota: Y quedé muy limpio, ¿para qué arriesgarme otra vez?
     [CUTAWAY: limpio]

✓ Guardado en: assets_temp/guiones/20260904_214530_guion.json

Próximo paso: python scripts/02_validador.py 20260904_214530
```

**Tiempo:** ~5-10 segundos  
**Costo:** ~$0.50 USD

⚠️ **Guarda el session_id** (ej: `20260904_214530`), lo necesitarás para el siguiente paso.

---

## Paso 6: Validar el guion ✅

Usa el `session_id` del paso anterior:

```bash
python scripts/02_validador.py 20260904_214530
```

**Output esperado (si aprueba):**

```
INFO     [02_validador] Validando guion (intento 1)...
INFO     [02_validador] Llamando a Claude API para validar guion...

============================================================
RESULTADO DE VALIDACIÓN
============================================================
✓ PASA - Comedia Universal
   El chiste sobre la limpieza del perro funciona tanto para niños
   (lo absurdo de bañarse una vez al año) como para adultos (la
   pereza universal de bañarse)

✓ PASA - Identificación
   Situación muy reconocible: la típica batalla de bañar a la mascota.
   Genera identificación inmediata con "así es mi perro"

✓ PASA - Lenguaje Panlatino
   Expresiones neutras que funcionan en toda Latinoamérica. Sin
   localismos ni groserías.

✓ PASA - Coherencia Personaje
   El estado de ánimo "sarcástico" de la mascota es consistente y
   potencia el remate final.

============================================================
DECISIÓN: Aprobar para producción
============================================================

INFO     [02_validador] ✓ ¡GUION APROBADO! Listo para pasar a producción.

✓ Guion final guardado en: assets_temp/guiones/20260904_214530_guion_final.json

Próximo paso: python scripts/03_imagenes.py 20260904_214530
```

**Tiempo:** ~5-10 segundos  
**Costo:** ~$0.25 USD

---

### Si el guion es rechazado ❌

El validador lo reescribirá automáticamente basándose en el feedback:

```
INFO     [02_validador] Guion rechazado. Reescribiendo (intento 2/3)...
```

Esto se repetirá hasta 2 veces. Si después de 3 intentos no se aprueba, deberás generar un nuevo guion desde cero.

---

## Paso 7: Usar el orquestador completo 🎬

En lugar de ejecutar cada script por separado, puedes usar el orquestador:

```bash
# Ejecutar etapas 1 y 1.5 automáticamente
python pipeline.py

# O con tema específico
python pipeline.py --tema "El gato no quiere ir al veterinario"
```

Esto ejecutará:
1. Generación de guion
2. Validación (con reintentos automáticos si falla)

**Output esperado:**

```
======================================================================
🎬 INICIANDO PIPELINE - Sesión: 20260904_215030
📍 Fase del proyecto: 1
🎯 Ejecutando hasta etapa: 2
======================================================================

▶️  ETAPA 1: Generación de guion
----------------------------------------------------------------------
[... logs de generación ...]
✓ Etapa 1 completada

▶️  ETAPA 2: Validación de guion
----------------------------------------------------------------------
[... logs de validación ...]
✓ Etapa 2 completada - Guion aprobado

======================================================================
✅ PIPELINE COMPLETADO EXITOSAMENTE
======================================================================
Sesión: 20260904_215030
Etapas completadas: 1, 2

Archivos generados:
  • Guion: assets_temp/guiones/20260904_215030_guion_final.json
  • Logs: logs/20260904_215030.json

💡 Próximos pasos (cuando estén disponibles):
   python pipeline.py --continuar 20260904_215030 --hasta-etapa 7
======================================================================
```

**Tiempo total:** ~15-30 segundos  
**Costo total:** ~$0.75 USD

---

## Paso 8: Revisar el guion aprobado 👀

```bash
# Ver el guion en formato legible
cat assets_temp/guiones/20260904_214530_guion_final.json | python -m json.tool
```

**Ejemplo de output:**

```json
{
  "personajes": [
    {
      "rol": "mascota",
      "especie": "perro",
      "estado_animo": "sarcástico"
    },
    {
      "rol": "papá"
    },
    {
      "rol": "hijo"
    }
  ],
  "escenario": "sala",
  "dialogo": [
    {
      "hablante": "papá",
      "linea": "¿Por qué el perro no quiere bañarse?"
    },
    {
      "hablante": "hijo",
      "linea": "Porque dice que ya se bañó... el año pasado"
    },
    {
      "hablante": "mascota",
      "linea": "Y quedé muy limpio, ¿para qué arriesgarme otra vez?",
      "cutaway": {
        "trigger": "limpio",
        "prompt_visual": "Perro cartoon muy sucio con barro por todas partes, moscas volando alrededor, olor visible con líneas onduladas, estilo cómico exagerado"
      }
    }
  ],
  "duracion_estimada_seg": 27
}
```

---

## Paso 9: Próximos pasos 🚀

### Para Fase 1 (actual)

Una vez que tengas guiones aprobados, el siguiente paso es desarrollar:

**Etapa 2: Generación de imágenes** (`scripts/03_imagenes.py`)
- Generar personajes según `docs/specs/style_bible.json`
- Generar fondo según escenario
- Generar cutaways
- Remover fondo de personajes

**Estado:** 🚧 En desarrollo

### Mientras tanto

Puedes:
1. **Generar más guiones** para tener un banco de ideas aprobadas
2. **Experimentar con diferentes temas** para ver qué funciona mejor
3. **Revisar la Style Bible** en `docs/specs/style_bible.json` para entender el estilo visual
4. **Leer la arquitectura** en `docs/architecture/ARQUITECTURA.md`

---

## 🐛 Troubleshooting

### "No se encontró la API key para anthropic"

**Solución:**
- Verifica que `.env` existe en la raíz del proyecto
- Verifica que la línea sea: `ANTHROPIC_API_KEY=sk-ant-...` (sin espacios, sin comillas)
- Verifica que la key sea válida en https://console.anthropic.com/settings/keys

### "ffmpeg: command not found"

**Solución:**
- Reinstala ffmpeg siguiendo el Paso 1
- Verifica que esté en PATH: `echo $PATH` (Linux/Mac) o `echo %PATH%` (Windows)
- Reinicia la terminal después de instalar

### "JSONDecodeError: Expecting value"

**Solución:**
- Claude no devolvió un JSON válido
- Revisa el log completo en `logs/{session_id}.json`
- Posibles causas:
  - API key inválida o sin créditos
  - Problema temporal de la API (reintenta en 1 minuto)
  - Prompt corrupto (poco probable)

### "Guion rechazado después de 2 reintentos"

**Solución:**
- Es normal, algunos temas son más difíciles
- Genera un nuevo guion con: `python scripts/01_guion.py`
- Intenta con un tema más concreto y cotidiano

### "Rate limit exceeded"

**Solución:**
- Has alcanzado el límite de requests por minuto de la API
- Espera 60 segundos y reintenta
- Claude API: 50 req/min
- Replicate: 10 req/min

---

## 📊 Resumen de costos hasta ahora

| Acción | Costo |
|--------|-------|
| Crear cuentas | $0 |
| Agregar créditos iniciales | $10 USD (Claude $5 + Replicate $5) |
| Generar 1 guion aprobado | ~$0.75 USD |
| **Total invertido** | **$10.75 USD** |

**Créditos restantes:** ~$9.25 USD (suficiente para 12+ guiones más)

---

## ✅ Checklist de configuración

- [ ] Python 3.10+ instalado
- [ ] ffmpeg instalado y en PATH
- [ ] Dependencias Python instaladas (`pip install -r requirements.txt`)
- [ ] Claude API key configurada en `.env`
- [ ] Replicate API token configurado en `.env`
- [ ] ElevenLabs API key configurada en `.env`
- [ ] Hedra API key configurada en `.env`
- [ ] `python scripts/test_setup.py` muestra todo ✅
- [ ] Primer guion generado exitosamente
- [ ] Primer guion validado y aprobado
- [ ] Guion final guardado en `assets_temp/guiones/`

---

¡Felicidades! 🎉 Has completado la configuración de Fase 1 y generado tu primer guion aprobado.

**Próximo paso:** Desarrollar Etapa 2 (generación de imágenes) o generar más guiones para tener un banco de contenido aprobado.
