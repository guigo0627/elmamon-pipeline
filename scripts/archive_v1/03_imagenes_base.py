#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de imágenes BASE para personajes
Genera solo las imágenes base (normal) que luego se usarán para crear variaciones
"""

import sys
import os
import json
import requests
import time
import base64
from pathlib import Path

# Configurar encoding UTF-8 en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, get_api_key

logger = setup_logger('imagenes_base')


def imagen_a_base64(ruta_imagen):
    """Convierte imagen local a base64 data URI"""
    with open(ruta_imagen, 'rb') as f:
        image_data = f.read()

    # Detectar tipo de imagen
    ext = Path(ruta_imagen).suffix.lower()
    if ext == '.png':
        mime = 'image/png'
    elif ext in ['.jpg', '.jpeg']:
        mime = 'image/jpeg'
    else:
        mime = 'image/png'

    b64 = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime};base64,{b64}"


def generar_imagen_base(prompt, imagen_referencia=None, output_path=None, api_key=None, modelo="schnell", prompt_strength=0.9):
    """
    Genera imagen base usando Replicate API
    Si imagen_referencia se proporciona, usa image-to-image
    """
    logger.info(f"🎨 Generando imagen base...")
    logger.info(f"   Prompt: {prompt[:100]}...")

    if imagen_referencia:
        logger.info(f"   📷 Usando imagen de referencia: {imagen_referencia}")

    url = "https://api.replicate.com/v1/predictions"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    # Seleccionar versión del modelo
    if modelo == "dev":
        version = "black-forest-labs/flux-dev"
        default_steps = 28
        logger.info(f"   🎨 Usando Flux Dev (más fidelidad a referencia)")
    else:
        version = "black-forest-labs/flux-schnell"
        default_steps = 4
        logger.info(f"   ⚡ Usando Flux Schnell (rápido)")

    # Preparar input
    input_data = {
        "prompt": prompt,
        "aspect_ratio": "9:16",
        "output_format": "png",
        "output_quality": 90,
        "num_inference_steps": default_steps,
        "go_fast": True if modelo == "schnell" else False
    }

    # Si hay imagen de referencia, agregarla
    if imagen_referencia:
        # Convertir imagen local a base64
        if os.path.exists(imagen_referencia):
            image_uri = imagen_a_base64(imagen_referencia)
            input_data["image"] = image_uri
            input_data["prompt_strength"] = prompt_strength
            logger.info(f"   🎚️ Prompt strength: {prompt_strength} (más alto = más parecido a referencia)")
        else:
            logger.warning(f"⚠️ Imagen de referencia no encontrada: {imagen_referencia}")

    data = {
        "version": version,
        "input": input_data
    }

    try:
        # Crear predicción
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 201:
            logger.error(f"❌ Error {response.status_code}: {response.text}")
            return False

        response.raise_for_status()
        prediction = response.json()

        prediction_id = prediction['id']
        logger.info(f"⏳ Predicción creada: {prediction_id}")

        # Esperar a que complete
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            time.sleep(2)

            status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()

            status = status_data['status']

            if status == 'succeeded':
                image_url = status_data['output'][0] if isinstance(status_data['output'], list) else status_data['output']
                logger.info(f"✅ Imagen generada: {image_url}")

                # Descargar y guardar
                img_response = requests.get(image_url)
                img_response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                logger.info(f"💾 Guardada en: {output_path}")
                return True

            elif status == 'failed':
                error = status_data.get('error', 'Unknown error')
                logger.error(f"❌ Generación falló: {error}")
                return False

            attempt += 1
            if attempt % 10 == 0:
                logger.info(f"⏳ Esperando... ({attempt}/{max_attempts}) Estado: {status}")

        logger.error(f"❌ Timeout esperando generación")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error en API: {e}")
        return False


def main():
    """Genera las imágenes BASE de personajes"""
    logger.info("=" * 60)
    logger.info("🎨 GENERANDO IMÁGENES BASE DE PERSONAJES")
    logger.info("=" * 60)

    # CONFIGURACIÓN: Cambiar aquí para probar diferentes modelos
    MODELO = "dev"  # "schnell" (rápido) o "dev" (mejor calidad)
    PROMPT_STRENGTH = 0.85  # 0.75-0.95 (más alto = más parecido a referencia)

    logger.info(f"🔧 Configuración:")
    logger.info(f"   - Modelo: {MODELO}")
    logger.info(f"   - Prompt Strength: {PROMPT_STRENGTH}")
    logger.info("")

    # Obtener API key
    api_key = get_api_key('replicate')
    if not api_key:
        logger.error("❌ No se encontró API key de Replicate")
        return False

    # Crear carpeta de salida
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output" / "personajes_base"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ruta a imágenes de referencia
    ref_gato = base_dir / "assets_temp" / "gato_referencia.png"
    ref_personajes = base_dir / "assets_temp" / "personajes_referencia.png"

    logger.info(f"📁 Carpeta de salida: {output_dir}")

    # ===== GATO BASE =====
    logger.info("\n" + "=" * 60)
    logger.info("🐱 GENERANDO: gato_normal.png")
    logger.info("=" * 60)

    gato_prompt = """simple cartoon drawing, character with cat-shaped head with big triangular ears on top,
large circular eyes, small nose dot, small mouth, WHITE skin color on face and hands (not orange),
human body wearing blue t-shirt and brown pants, standing neutral pose, arms at sides,
thick black outlines 3-4px width, flat colors, clean simple style, no shadows,
vertical format 9:16, white background"""

    gato_output = output_dir / "gato_normal.png"

    if ref_gato.exists():
        logger.info("📷 Usando imagen de referencia del gato")
        gato_ok = generar_imagen_base(gato_prompt, str(ref_gato), str(gato_output), api_key, MODELO, PROMPT_STRENGTH)
    else:
        logger.warning("⚠️ Imagen de referencia no encontrada, generando sin referencia")
        gato_ok = generar_imagen_base(gato_prompt, None, str(gato_output), api_key, MODELO)

    if not gato_ok:
        logger.error("❌ Falló generación de gato base")
        return False

    logger.info("⏳ Esperando 3 segundos antes de siguiente imagen...")
    time.sleep(3)

    # ===== MAMÁ BASE =====
    logger.info("\n" + "=" * 60)
    logger.info("👩 GENERANDO: mamá_normal.png")
    logger.info("=" * 60)

    mama_prompt = """simple cartoon drawing, woman with WHITE circular head, no hair (bald),
large circular eyes, small nose, small mouth, WHITE skin on face and hands,
human body wearing yellow t-shirt and gray pants, standing neutral pose, arms at sides,
thick black outlines 3-4px width, flat colors, clean simple style, no shadows,
vertical format 9:16, white background"""

    mama_output = output_dir / "mama_normal.png"

    if ref_personajes.exists():
        logger.info("📷 Usando imagen de referencia de personajes")
        mama_ok = generar_imagen_base(mama_prompt, str(ref_personajes), str(mama_output), api_key, MODELO, PROMPT_STRENGTH)
    else:
        logger.warning("⚠️ Imagen de referencia no encontrada, generando sin referencia")
        mama_ok = generar_imagen_base(mama_prompt, None, str(mama_output), api_key, MODELO)

    if not mama_ok:
        logger.error("❌ Falló generación de mamá base")
        return False

    # ===== RESUMEN =====
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN")
    logger.info("=" * 60)
    logger.info(f"✅ Gato base: {gato_output}")
    logger.info(f"✅ Mama base: {mama_output}")
    logger.info("")
    logger.info("🎯 Siguiente paso: Aprobar bases antes de generar variaciones")
    logger.info("=" * 60)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
