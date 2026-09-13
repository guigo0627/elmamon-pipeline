#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Background Downloader
Descarga imágenes reales de Pexels según el escenario analizado
"""

import sys
import os
from pathlib import Path
import json
import requests
import ssl

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('backgrounds')

# Deshabilitar SSL warnings (PC corporativo)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# PEXELS API (gratuita, no requiere key para búsqueda básica)
PEXELS_API = "https://api.pexels.com/v1/search"

# Mapeo de escenarios a búsquedas
ESCENARIOS = {
    'sala_casa': {
        'queries': ['modest living room', 'simple home interior', 'basic living room'],
        'orientation': 'landscape',
        'size': 'large'
    },
    'cocina': {
        'queries': ['simple kitchen', 'basic kitchen interior', 'modest kitchen'],
        'orientation': 'landscape',
        'size': 'large'
    },
    'cuarto': {
        'queries': ['simple bedroom', 'basic bedroom', 'modest bedroom interior'],
        'orientation': 'landscape',
        'size': 'large'
    },
    'baño': {
        'queries': ['simple bathroom', 'basic bathroom interior'],
        'orientation': 'landscape',
        'size': 'large'
    },
    'supermercado': {
        'queries': ['supermarket aisle', 'grocery store interior'],
        'orientation': 'landscape',
        'size': 'large'
    },
    'gym': {
        'queries': ['gym interior', 'fitness center', 'workout space'],
        'orientation': 'landscape',
        'size': 'large'
    }
}


def download_background_pexels(escenario, output_path, pexels_key=None):
    """
    Descarga background de Pexels

    Args:
        escenario: Tipo de escenario (sala_casa, cocina, etc)
        output_path: Donde guardar la imagen
        pexels_key: API key de Pexels (opcional para búsquedas básicas)
    """
    if escenario not in ESCENARIOS:
        logger.warning(f"Escenario '{escenario}' no reconocido, usando 'sala_casa'")
        escenario = 'sala_casa'

    config = ESCENARIOS[escenario]
    query = config['queries'][0]

    logger.info(f"🔍 Buscando: {query}")

    # Usar Unsplash Source (sin API key necesaria)
    # Formato: https://source.unsplash.com/1920x1080/?query
    unsplash_url = f"https://source.unsplash.com/1920x1080/?{query.replace(' ', ',')}"

    try:
        logger.info("📥 Descargando desde Unsplash...")
        response = requests.get(unsplash_url, timeout=30, verify=False)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✅ Background descargado: {output_path}")
            logger.info(f"   Tamaño: {len(response.content) / 1024:.1f} KB")
            return True
        else:
            logger.error(f"❌ Error: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error descargando: {e}")
        return False


def get_background_for_video(animation_plan_path, output_dir):
    """
    Lee el animation_plan y descarga el background apropiado

    Args:
        animation_plan_path: Ruta al animation_plan.json
        output_dir: Directorio donde guardar el background
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    logger.info("=" * 70)
    logger.info("🖼️  DESCARGA DE BACKGROUND")
    logger.info("=" * 70)

    # Leer animation plan
    with open(animation_plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    # Extraer escenario recomendado
    if 'background_analysis' in plan['analysis']:
        escenario = plan['analysis']['background_analysis']['recommended_setting']
        logger.info(f"📋 Escenario recomendado: {escenario}")
    else:
        escenario = 'sala_casa'
        logger.info(f"📋 Usando escenario por defecto: {escenario}")

    # Descargar
    output_path = output_dir / f"background_{escenario}.jpg"

    if output_path.exists():
        logger.info(f"ℹ️  Background ya existe: {output_path}")
        return str(output_path)

    success = download_background_pexels(escenario, output_path)

    if success:
        logger.info("=" * 70)
        logger.info("✅ BACKGROUND LISTO")
        logger.info("=" * 70)
        return str(output_path)
    else:
        logger.error("❌ No se pudo descargar background")
        return None


def main():
    """Test del downloader"""
    base_dir = Path(__file__).parent.parent.parent
    animation_plan = base_dir / "output" / "001-20260910" / "animation_plan.json"
    output_dir = base_dir / "output" / "001-20260910" / "backgrounds"

    if not animation_plan.exists():
        logger.error(f"❌ animation_plan.json no encontrado: {animation_plan}")
        return False

    background_path = get_background_for_video(animation_plan, output_dir)

    if background_path:
        logger.info(f"\n🎉 Background guardado en: {background_path}")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
