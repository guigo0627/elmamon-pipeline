# 🚀 Inicio Rápido - elmamon-pipeline

## Paso 1: Instalar dependencias

```bash
pip install -r requirements.txt
```

## Paso 2: Configurar API keys

1. Copia la plantilla de configuración:
```bash
cp .env.template .env
```

2. Edita `.env` y agrega tus API keys:

### APIs necesarias para Fase 1:

#### 1️⃣ Claude API (Anthropic) - OBLIGATORIA
```
https://console.anthropic.com/
→ Settings → API Keys → Create Key
→ Copiar y pegar en: ANTHROPIC_API_KEY=
```

#### 2️⃣ Replicate API - OBLIGATORIA
```
https://replicate.com/
→ Account → API tokens → Create token
→ Copiar y pegar en: REPLICATE_API_TOKEN=
```

#### 3️⃣ ElevenLabs API - OBLIGATORIA
```
https://elevenlabs.io/
→ Sign up (Plan Free: 10k caracteres/mes)
→ Profile → API Key
→ Copiar y pegar en: ELEVENLABS_API_KEY=
```

#### 4️⃣ Hedra API - OBLIGATORIA
```
https://www.hedra.com/
→ Sign up (Plan Free: ~7 videos/mes)
→ Dashboard → API
→ Copiar y pegar en: HEDRA_API_KEY=
```

## Paso 3: Verificar instalación (opcional)

```bash
python scripts/test_setup.py
```

Este script verificará:
- ✅ Que todas las API keys estén configuradas
- ✅ Que ffmpeg esté instalado
- ✅ Que las carpetas necesarias existan
- ✅ Que las dependencias estén instaladas

## Paso 4: Generar tu primer guion

```bash
python scripts/01_guion.py
```

Esto generará un guion aleatorio siguiendo todas las reglas del formato.

**Output esperado:**
```
[INFO] Iniciando generación de guion para sesión 20260904_211456
[INFO] Llamando a Claude API para generar guion...
[INFO] ✓ Guion generado exitosamente: assets_temp/guiones/20260904_211456_guion.json
[INFO]   - Personajes: 3
[INFO]   - Líneas de diálogo: 4
[INFO]   - Escenario: sala
[INFO]   - Duración estimada: 27 seg
```

## Paso 5: Validar el guion

```bash
python scripts/02_validador.py 20260904_211456
```

Reemplaza `20260904_211456` con el session_id de tu guion.

**Output esperado:**
```
============================================================
RESULTADO DE VALIDACIÓN
============================================================
✓ PASA - Comedia Universal
   El chiste funciona para ambos rangos de edad...
✓ PASA - Identificación
   La situación es reconocible...
✓ PASA - Lenguaje Panlatino
   Las expresiones son neutras...
✓ PASA - Coherencia Personaje
   El estado de ánimo es consistente...

============================================================
DECISIÓN: Aprobar para producción
============================================================

✓ ¡GUION APROBADO! Listo para pasar a producción.
```

## Próximos pasos

Una vez que tengas un guion aprobado:

1. **Paso 3**: Generar imágenes (personajes, fondo, cutaways) → `03_imagenes.py` (en desarrollo)
2. **Paso 4**: Generar audio → `04_audio.py` (en desarrollo)
3. **Paso 5**: Animar personajes → `05_animacion.py` (en desarrollo)
4. **Paso 6**: Montaje final → `06_montaje.py` (en desarrollo)

## 🐛 Problemas comunes

### "No se encontró la API key para anthropic"
→ Verifica que `.env` existe y tiene `ANTHROPIC_API_KEY=sk-ant-...`

### "ffmpeg: command not found"
→ Instala ffmpeg:
- Windows: `winget install ffmpeg`
- Linux: `sudo apt install ffmpeg`
- Mac: `brew install ffmpeg`

### "JSONDecodeError: Expecting value"
→ Claude no devolvió un JSON válido. Revisa `logs/{session_id}.json` para ver la respuesta completa.

## 💡 Tips

- **Generar guion con tema específico:**
  ```bash
  python scripts/01_guion.py "El gato no quiere bañarse"
  ```

- **Ver logs detallados:**
  ```bash
  cat logs/{session_id}.json
  ```

- **Limpiar archivos temporales:**
  ```bash
  rm -rf assets_temp/*
  ```

## 📊 Límites de Fase 1 (planes gratuitos)

- **ElevenLabs Free**: 10,000 caracteres/mes ≈ 10 videos
- **Hedra Free**: ~7 videos/mes
- **Replicate**: Pago por uso (~$0.05-0.10 por imagen)
- **Claude API**: Pago por uso (~$0.50-1.00 por guion+validación)

**Total estimado Fase 1**: ~$10-15/mes para 10 videos de prueba

---

¿Listo para empezar? 🚀

```bash
python scripts/01_guion.py
```
