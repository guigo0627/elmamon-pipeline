#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 4: Background Manager
Gestiona backgrounds reales por escenario (sala, cocina, gym, etc.)
"""

import sys
import os
from pathlib import Path
import json
import random

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('bg_manager')

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Mapeo de escenarios a carpetas
ESCENARIOS_MAP = {
    'sala_casa': 'sala_casa',
    'living_room': 'sala_casa',
    'sala': 'sala_casa',
    'cocina': 'cocina',
    'kitchen': 'cocina',
    'cuarto': 'cuarto',
    'bedroom': 'cuarto',
    'habitacion': 'cuarto',
    'gym': 'gym',
    'gimnasio': 'gym',
    'supermercado': 'supermercado',
    'supermarket': 'supermercado',
    'bano': 'bano',
    'bathroom': 'bano',
}


def get_background_for_scenario(scenario, assets_dir=None):
    """
    Obtiene un background aleatorio para el escenario dado

    Args:
        scenario: Nombre del escenario (ej: 'sala_casa', 'cocina')
        assets_dir: Ruta a assets/backgrounds/ (opcional)

    Returns:
        Path: Ruta al background seleccionado
        None: Si no hay backgrounds disponibles
    """
    if assets_dir is None:
        base_dir = Path(__file__).parent.parent.parent
        assets_dir = base_dir / "assets" / "backgrounds"

    # Normalizar nombre del escenario
    scenario_normalized = ESCENARIOS_MAP.get(scenario.lower(), scenario.lower())

    scenario_dir = assets_dir / scenario_normalized

    if not scenario_dir.exists():
        logger.warning(f"⚠️  Directorio de escenario no existe: {scenario_dir}")
        logger.info(f"   Creando: {scenario_dir}")
        scenario_dir.mkdir(parents=True, exist_ok=True)
        return None

    # Buscar imágenes en el directorio
    images = list(scenario_dir.glob("*.jpg")) + \
             list(scenario_dir.glob("*.jpeg")) + \
             list(scenario_dir.glob("*.png"))

    if not images:
        logger.warning(f"⚠️  No hay imágenes en: {scenario_dir}")
        logger.info(f"   Por favor agrega imágenes REALES de {scenario_normalized}")
        return None

    # Seleccionar aleatoriamente
    selected = random.choice(images)
    logger.info(f"📷 Background seleccionado: {selected.name}")

    return selected


def prepare_background(bg_path, output_size=(1080, 1920)):
    """
    Prepara background para formato 9:16

    Args:
        bg_path: Ruta a la imagen
        output_size: Tamaño de salida (width, height)

    Returns:
        PIL Image redimensionado y recortado
    """
    if not PIL_AVAILABLE:
        logger.error("❌ PIL no disponible")
        return None

    bg = Image.open(bg_path).convert('RGB')

    target_w, target_h = output_size
    bg_ratio = bg.width / bg.height
    target_ratio = target_w / target_h

    # Redimensionar manteniendo aspecto
    if bg_ratio > target_ratio:
        # Background más ancho, crop horizontal
        new_height = target_h
        new_width = int(new_height * bg_ratio)
        bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop centro
        left = (new_width - target_w) // 2
        bg = bg.crop((left, 0, left + target_w, target_h))
    else:
        # Background más alto, crop vertical
        new_width = target_w
        new_height = int(new_width / bg_ratio)
        bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop centro
        top = (new_height - target_h) // 2
        bg = bg.crop((0, top, target_w, top + target_h))

    logger.info(f"   Redimensionado: {bg.size}")

    return bg


def get_background_for_video(animation_plan_path, output_dir):
    """
    Obtiene y prepara el background para un video según el animation_plan

    Args:
        animation_plan_path: Ruta al animation_plan.json
        output_dir: Directorio donde guardar el background preparado

    Returns:
        Path: Ruta al background preparado
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    logger.info("=" * 70)
    logger.info("🖼️  BACKGROUND MANAGER")
    logger.info("=" * 70)

    # Leer animation plan
    with open(animation_plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    # Extraer escenario recomendado
    if 'background_analysis' in plan['analysis']:
        scenario = plan['analysis']['background_analysis']['recommended_setting']
        logger.info(f"📋 Escenario recomendado: {scenario}")
    else:
        scenario = 'sala_casa'
        logger.warning(f"⚠️  No hay background_analysis, usando: {scenario}")

    # Obtener background
    bg_path = get_background_for_scenario(scenario)

    if bg_path is None:
        logger.error("❌ No se pudo obtener background")
        logger.info("")
        logger.info("💡 SOLUCIÓN:")
        logger.info(f"   1. Descarga imágenes REALES de {scenario}")
        logger.info(f"   2. Guárdalas en: assets/backgrounds/{ESCENARIOS_MAP.get(scenario, scenario)}/")
        logger.info(f"   3. Formatos: .jpg, .jpeg, .png")
        logger.info("")
        return None

    # Preparar background
    logger.info("🔄 Preparando background...")
    bg_prepared = prepare_background(bg_path, output_size=(1080, 1920))

    if bg_prepared is None:
        return None

    # Guardar
    output_path = output_dir / f"background_{scenario}.png"
    bg_prepared.save(output_path, quality=95)

    logger.info(f"💾 Background guardado: {output_path}")
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ BACKGROUND LISTO")
    logger.info("=" * 70)

    return output_path


def main():
    """Test del background manager"""
    base_dir = Path(__file__).parent.parent.parent
    animation_plan = base_dir / "output" / "001-20260910" / "animation_plan.json"
    output_dir = base_dir / "output" / "001-20260910" / "backgrounds"

    if not animation_plan.exists():
        logger.error(f"❌ animation_plan.json no encontrado: {animation_plan}")
        return False

    background_path = get_background_for_video(animation_plan, output_dir)

    if background_path:
        logger.info(f"\n🎉 Background listo: {background_path}")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
