#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Backgrounds con Flux
Input:  animation_plan.json (con background_analysis)
Output: Imagen de fondo real con Replicate/Flux
"""

import sys
import os
from pathlib import Path
import json
import time

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('bg_generator')

try:
    import replicate
    # Fix SSL para PC corporativo
    import ssl
    import httpx
    ssl._create_default_https_context = ssl._create_unverified_context

    # Monkey patch httpx para deshabilitar verificación
    _original_httpx_client_init = httpx.Client.__init__
    def patched_init(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_httpx_client_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_init

    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    logger.error("❌ Replicate no instalado")

from dotenv import load_dotenv
load_dotenv()

REPLICATE_API_KEY = os.getenv('REPLICATE_API_TOKEN')

# Prompts optimizados para Flux
BACKGROUND_PROMPTS = {
    'sala_casa': {
        'prompt': 'HIGH QUALITY PHOTOGRAPH of a real modest living room interior in a middle-class Latin American household, simple beige or brown fabric sofa, basic wooden TV stand with small television, painted cement walls in warm beige or light yellow tones, simple family photos on walls, basic floor lamp, basic coffee table, ceramic floor tiles, natural daylight from window, real world photography, photorealistic, real home interior, documentary style photography, 4k photograph',
        'negative': 'cartoon, anime, drawing, illustration, painting, rendered, 3d render, cgi, animated, luxury apartment, modern minimalist, designer furniture, mansion, palace, artificial, digital art, art style'
    },
    'cocina': {
        'prompt': 'Photo of a simple kitchen in a middle-class Latin American home. Basic cabinets, simple stove, small refrigerator, tiled walls, organized countertop, realistic photography, real interior',
        'negative': 'cartoon, animation, illustration, luxury, modern minimalist, designer kitchen'
    },
    'cuarto': {
        'prompt': 'Photo of a modest bedroom in a middle-class home. Simple bed with basic bedding, small nightstand, painted walls, basic closet, realistic photography',
        'negative': 'cartoon, luxury, modern minimalist'
    }
}


def generate_background_flux(escenario, output_path):
    """
    Genera background con Flux Schnell (rápido y barato)

    Args:
        escenario: Tipo de escenario
        output_path: Donde guardar
    """
    if not REPLICATE_AVAILABLE:
        logger.error("❌ Replicate no disponible")
        return False

    if not REPLICATE_API_KEY:
        logger.error("❌ REPLICATE_API_TOKEN no configurado")
        return False

    if escenario not in BACKGROUND_PROMPTS:
        logger.warning(f"Escenario '{escenario}' no tiene prompt, usando 'sala_casa'")
        escenario = 'sala_casa'

    config = BACKGROUND_PROMPTS[escenario]

    logger.info(f"🎨 Generando fondo: {escenario}")
    logger.info(f"   Prompt: {config['prompt'][:80]}...")

    try:
        # Flux Schnell (más rápido y barato)
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": config['prompt'],
                "num_outputs": 1,
                "aspect_ratio": "16:9",  # Horizontal para background
                "output_format": "png",
                "output_quality": 90,
                "num_inference_steps": 4,  # Schnell es rápido
            }
        )

        # Descargar imagen
        import requests
        image_url = output[0] if isinstance(output, list) else output

        logger.info("📥 Descargando imagen generada...")
        response = requests.get(image_url, timeout=60)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✅ Background generado: {output_path}")
            logger.info(f"   Tamaño: {len(response.content) / 1024:.1f} KB")
            logger.info(f"   Costo: ~$0.003 USD")
            return True
        else:
            logger.error(f"❌ Error descargando: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Genera background para video 001"""
    base_dir = Path(__file__).parent.parent.parent
    animation_plan_path = base_dir / "output" / "001-20260910" / "animation_plan.json"
    output_dir = base_dir / "output" / "001-20260910" / "backgrounds"
    output_dir.mkdir(exist_ok=True, parents=True)

    logger.info("=" * 70)
    logger.info("🎨 GENERACIÓN DE BACKGROUND CON FLUX")
    logger.info("=" * 70)

    if not animation_plan_path.exists():
        logger.error(f"❌ animation_plan.json no encontrado")
        return False

    # Leer plan
    with open(animation_plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    # Obtener escenario
    if 'background_analysis' in plan['analysis']:
        escenario = plan['analysis']['background_analysis']['recommended_setting']
        logger.info(f"📋 Escenario: {escenario}")
    else:
        escenario = 'sala_casa'
        logger.info(f"📋 Escenario por defecto: {escenario}")

    # Output
    output_path = output_dir / f"background_{escenario}.png"

    if output_path.exists():
        logger.info(f"ℹ️  Background ya existe: {output_path}")
        return True

    # Generar
    success = generate_background_flux(escenario, output_path)

    if success:
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ BACKGROUND LISTO")
        logger.info("=" * 70)
        logger.info(f"📁 {output_path}")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
