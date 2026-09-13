#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de VARIACIONES de personajes
Toma imágenes base y genera variaciones con diferentes expresiones
manteniendo TOTAL consistencia visual (color, estilo, proporciones)
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

logger = setup_logger('variaciones')


def imagen_a_base64(ruta_imagen):
    """Convierte imagen local a base64 data URI"""
    with open(ruta_imagen, 'rb') as f:
        image_data = f.read()

    ext = Path(ruta_imagen).suffix.lower()
    if ext == '.png':
        mime = 'image/png'
    elif ext in ['.jpg', '.jpeg', '.jfif']:
        mime = 'image/jpeg'
    else:
        mime = 'image/png'

    b64 = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime};base64,{b64}"


# Mapeo de expresiones a descripciones
EXPRESIONES = {
    'normal': 'neutral calm expression, arms at sides',
    'preguntando': 'curious questioning expression, one arm pointing forward',
    'confundida': 'confused puzzled expression, one hand on head scratching',
    'sorprendida': 'very surprised shocked expression, both arms raised up',
    'feliz': 'very happy smiling expression, arms slightly raised',
    'triste': 'sad disappointed expression, arms down',
    'enojada': 'angry frustrated expression, arms crossed or at sides',
    'pensando': 'thinking contemplating expression, hand on chin',
}


def generar_variacion(base_image_path, expresion, output_path, api_key,
                      modelo="schnell", prompt_strength=0.95):
    """
    Genera variación de personaje base cambiando SOLO la expresión

    Args:
        base_image_path: Ruta a imagen base
        expresion: Tipo de expresión (ver EXPRESIONES dict)
        output_path: Donde guardar resultado
        modelo: "schnell" o "dev"
        prompt_strength: 0.90-0.98 (más alto = más similar a base)
    """
    logger.info(f"🎭 Generando variación: {expresion}")
    logger.info(f"   📷 Base: {Path(base_image_path).name}")

    # Obtener descripción de expresión
    expresion_desc = EXPRESIONES.get(expresion, EXPRESIONES['normal'])

    # Prompt MUY ESPECÍFICO para mantener consistencia
    prompt = f"""EXACT same character, IDENTICAL in every way:
- Keep exact same colors
- Keep exact same clothing
- Keep exact same style and proportions
- Keep exact same body shape
- Keep exact same background
ONLY change: {expresion_desc}
Do not add or remove any details, keep everything identical except facial expression and arm position"""

    logger.info(f"   🎚️ Strength: {prompt_strength} (mantiene {int(prompt_strength*100)}% de la base)")

    # Convertir base a base64
    try:
        image_uri = imagen_a_base64(base_image_path)
    except Exception as e:
        logger.error(f"❌ Error leyendo imagen base: {e}")
        return False

    # Seleccionar modelo
    if modelo == "dev":
        version = "black-forest-labs/flux-dev"
        default_steps = 28
    else:
        version = "black-forest-labs/flux-schnell"
        default_steps = 4

    # Preparar request
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "version": version,
        "input": {
            "image": image_uri,
            "prompt": prompt,
            "prompt_strength": prompt_strength,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 90,
            "num_inference_steps": default_steps,
            "go_fast": True if modelo == "schnell" else False
        }
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

        # Esperar resultado
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
                logger.info(f"✅ Variación generada: {image_url}")

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
                logger.info(f"⏳ Esperando... ({attempt}/{max_attempts})")

        logger.error(f"❌ Timeout")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error en API: {e}")
        return False


def main():
    """Prueba de generación de variaciones"""
    logger.info("=" * 60)
    logger.info("🎭 GENERADOR DE VARIACIONES")
    logger.info("=" * 60)

    # Configuración
    MODELO = "schnell"  # "schnell" (rápido) o "dev"
    PROMPT_STRENGTH = 0.95  # 0.90-0.98 (más alto = más consistencia)

    logger.info(f"🔧 Configuración:")
    logger.info(f"   - Modelo: {MODELO}")
    logger.info(f"   - Strength: {PROMPT_STRENGTH}")
    logger.info("")

    # API key
    api_key = get_api_key('replicate')
    if not api_key:
        logger.error("❌ No se encontró API key de Replicate")
        return False

    # Rutas
    base_dir = Path(__file__).parent.parent
    bases_dir = base_dir / "assets" / "personajes_base"
    output_dir = base_dir / "output" / "variaciones_prueba"
    output_dir.mkdir(parents=True, exist_ok=True)

    # PRUEBA: Generar 2 variaciones de mama_base
    mama_base = bases_dir / "mama_base.png"

    if not mama_base.exists():
        logger.error(f"❌ No se encontró: {mama_base}")
        return False

    logger.info(f"📁 Base encontrada: {mama_base.name}")
    logger.info("")

    # Variación 1: Sorprendida
    logger.info("=" * 60)
    logger.info("🎭 VARIACIÓN 1: Sorprendida")
    logger.info("=" * 60)

    output1 = output_dir / "mama_sorprendida.png"
    ok1 = generar_variacion(
        str(mama_base),
        "sorprendida",
        str(output1),
        api_key,
        MODELO,
        PROMPT_STRENGTH
    )

    if not ok1:
        logger.error("❌ Falló variación 1")
        return False

    logger.info("⏳ Esperando 3 segundos...")
    time.sleep(3)

    # Variación 2: Confundida
    logger.info("")
    logger.info("=" * 60)
    logger.info("🎭 VARIACIÓN 2: Confundida")
    logger.info("=" * 60)

    output2 = output_dir / "mama_confundida.png"
    ok2 = generar_variacion(
        str(mama_base),
        "confundida",
        str(output2),
        api_key,
        MODELO,
        PROMPT_STRENGTH
    )

    if not ok2:
        logger.error("❌ Falló variación 2")
        return False

    # Resumen
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 RESUMEN")
    logger.info("=" * 60)
    logger.info(f"✅ Base: {mama_base}")
    logger.info(f"✅ Variación 1 (sorprendida): {output1}")
    logger.info(f"✅ Variación 2 (confundida): {output2}")
    logger.info("")
    logger.info("🎯 Revisa las imágenes para verificar consistencia:")
    logger.info("   - ¿Mantiene el mismo color de ropa?")
    logger.info("   - ¿Mantiene el mismo cabello?")
    logger.info("   - ¿Mantiene las mismas proporciones?")
    logger.info("   - ¿Solo cambió la expresión?")
    logger.info("=" * 60)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
