# Integración con Facebook

Guía completa para publicar videos automáticamente en Facebook.

---

## 🚀 Configuración Inicial

### 1. Obtener Credenciales de Facebook

#### A. Crear App de Facebook
1. Ir a [Facebook Developers](https://developers.facebook.com/)
2. Crear una nueva App
3. Seleccionar tipo: "Business"
4. Configurar permisos: `pages_manage_posts`, `publish_video`, `pages_read_engagement`

#### B. Obtener Page ID
1. Ir a tu página de Facebook
2. Click en "About" / "Acerca de"
3. Scroll abajo, copiar "Page ID"

#### C. Obtener Access Token
1. Ir a [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Seleccionar tu App
3. Seleccionar tu Página
4. Agregar permisos: `pages_manage_posts`, `publish_video`
5. Click "Generate Access Token"
6. Copiar el token

#### D. Generar Token de Larga Duración (60 días)
```bash
curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

---

## ⚙️ Configurar el Proyecto

### 1. Crear archivo .env

Copiar `.env.example` a `.env`:

```bash
cp .env.example .env
```

Editar `.env` y completar:

```env
FACEBOOK_PAGE_ID=123456789012345
FACEBOOK_ACCESS_TOKEN=EAAxxxxxxxxxxxxx
```

### 2. Instalar dependencias

```bash
pip install requests python-dotenv
```

---

## 📤 Publicar Videos

### Publicación Manual

```bash
python scripts/social/facebook_publisher.py
```

### Publicación con Parámetros Personalizados

```python
from scripts.social.facebook_publisher import FacebookPublisher

publisher = FacebookPublisher(PAGE_ID, ACCESS_TOKEN)

result = publisher.upload_video(
    video_path="output/003-20260912/scene_00s_titled_final.mp4",
    title="Cuando mi esposa me pide perdón... 😅",
    description="¿Les pasa o solo a mí? 😂",
    tags=["comedia", "pareja", "situaciones", "humor"]
)
```

### Programar Publicación Futura

```python
import time
from datetime import datetime, timedelta

# Programar para mañana a las 12:00 PM
tomorrow = datetime.now() + timedelta(days=1)
scheduled_time = tomorrow.replace(hour=12, minute=0, second=0)
timestamp = int(scheduled_time.timestamp())

publisher.schedule_video(
    video_path="video.mp4",
    title="Título",
    description="Descripción",
    scheduled_time=timestamp,
    tags=["tag1", "tag2"]
)
```

---

## 🎨 Optimizar Página

### Ver Información Actual

```bash
python scripts/social/facebook_page_optimizer.py
```

### Actualizar Descripción

El script actualiza automáticamente:
- ✅ About (descripción corta)
- ✅ Description (descripción larga)
- ✅ Website URL

### Subir Imágenes

```python
from scripts.social.facebook_page_optimizer import FacebookPageOptimizer

optimizer = FacebookPageOptimizer(PAGE_ID, ACCESS_TOKEN)

# Foto de perfil (320x320px)
optimizer.upload_profile_picture("assets/logo_320x320.png")

# Portada (820x312px)
optimizer.upload_cover_photo("assets/banner_820x312.png")
```

---

## 🤖 Automatización

### Script de Pipeline Completo

Crear `scripts/publish_pipeline.py`:

```python
#!/usr/bin/env python3
"""Pipeline completo: generar + metadata + publicar"""

from pathlib import Path
import subprocess
import os

# 1. Generar video (ya hecho)
video_dir = Path("output/003-20260912")

# 2. Agregar metadata
subprocess.run([
    "python", "scripts/pipeline_v2/10_add_metadata.py",
    str(video_dir)
])

# 3. Publicar a Facebook
from scripts.social.facebook_publisher import FacebookPublisher

PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

publisher = FacebookPublisher(PAGE_ID, ACCESS_TOKEN)

video_path = video_dir / "scene_00s_titled_final.mp4"

result = publisher.upload_video(
    video_path=video_path,
    title="Cuando mi esposa me pide perdón... 😅",
    description="¿Les pasa o solo a mí? 😂\n\n👉 Dale like si te identificas",
    tags=["comedia", "pareja", "situaciones", "humor", "viral"]
)

print(f"✅ Video publicado: {result.get('id')}")
```

### Programar con Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Publicar diariamente a las 12:00 PM y 7:00 PM
0 12 * * * cd /path/to/project && python scripts/publish_pipeline.py
0 19 * * * cd /path/to/project && python scripts/publish_pipeline.py
```

### Programar con Task Scheduler (Windows)

1. Abrir "Task Scheduler"
2. Create Task
3. Trigger: Daily, 12:00 PM
4. Action: `python scripts/publish_pipeline.py`

---

## 📊 Estrategia de Contenido

Ver documento completo: [`docs/FACEBOOK_SEO_STRATEGY.md`](FACEBOOK_SEO_STRATEGY.md)

### Resumen

- **Frecuencia:** 1-2 videos diarios
- **Horarios:** 12:00 PM, 7:00 PM
- **Hashtags:** 5-8 por post
- **CTA:** Siempre incluir call-to-action

### Plantilla de Post

```
[Emoji] [Título gancho]

[Descripción 1-2 líneas]

👉 Dale like si te identificas
💬 Comenta tu experiencia
🔄 Comparte con quien le pasa

#Hashtag1 #Hashtag2 #Hashtag3
```

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE

- **NO** hacer commit de `.env`
- **NO** compartir el Access Token
- Renovar token cada 60 días
- Usar variables de entorno en producción

### .gitignore

```gitignore
.env
*.env.local
credentials/
tokens/
```

---

## 🐛 Troubleshooting

### Error: "Invalid OAuth Token"
- Token expiró → Generar uno nuevo
- Permisos insuficientes → Verificar en Graph API Explorer

### Error: "Upload Failed"
- Video muy grande → Máximo 10 GB
- Formato no soportado → Usar MP4 H.264

### Error: "Rate Limit"
- Demasiadas requests → Esperar 1 hora
- Límite de videos → Máximo 75 videos/día

---

## 📈 Métricas

### Verificar Rendimiento

```python
# Obtener insights del video
url = f"https://graph.facebook.com/v18.0/{VIDEO_ID}/video_insights"
params = {
    'access_token': ACCESS_TOKEN,
    'metric': 'total_video_views,total_video_views_unique'
}
response = requests.get(url, params=params)
print(response.json())
```

---

## 📚 Referencias

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Video Upload Reference](https://developers.facebook.com/docs/video-api/guides/publishing)
- [Access Token Debug](https://developers.facebook.com/tools/debug/accesstoken/)

---

*Última actualización: 2026-09-12*
