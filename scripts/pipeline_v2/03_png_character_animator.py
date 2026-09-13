#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 3B: PNG Character Animator
Sistema de animación de personajes PNG con lip sync
Input:  Imágenes PNG de personajes base
Output: Frames animados con lip sync
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('png_animator')

# Configuración de bocas por personaje (DETECCIÓN INTELIGENTE - Factor 0.3)
MOUTH_CONFIG = {
    'mama': {
        'center_x': 536,  # Detectado vía ojos
        'center_y': 583,  # Factor 0.3 (dentro de cara)
        'closed': {'width': 50, 'height': 6},
        'semi': {'width': 35, 'height': 28},
        'open': {'width': 42, 'height': 48}
    },
    'papa': {
        'center_x': 515,  # Detectado vía ojos
        'center_y': 725,  # Factor 0.3 (dentro de cara)
        'closed': {'width': 48, 'height': 6},
        'semi': {'width': 32, 'height': 26},
        'open': {'width': 40, 'height': 45}
    }
}


def load_character_png(character_type, assets_dir):
    """
    Carga imagen PNG de personaje

    Args:
        character_type: 'mama' o 'papa'
        assets_dir: Directorio de assets

    Returns:
        PIL.Image: Imagen del personaje
    """
    assets_dir = Path(assets_dir)

    if character_type == 'mama':
        img_path = assets_dir / "personajes_base" / "mama_base.png"
    elif character_type == 'papa':
        img_path = assets_dir / "personajes_base" / "papá_sumiso.png"
    else:
        raise ValueError(f"Tipo de personaje no válido: {character_type}")

    if not img_path.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {img_path}")

    img = Image.open(img_path).convert('RGBA')
    return img


def draw_mouth(img, character_type, mouth_state):
    """
    Dibuja boca sobre el personaje PNG según estado de lip sync

    Args:
        img: PIL.Image del personaje
        character_type: 'mama' o 'papa'
        mouth_state: 'closed', 'semi', 'open'

    Returns:
        PIL.Image: Imagen con boca animada
    """
    # Crear copia para no modificar original
    img_copy = img.copy()
    draw = ImageDraw.Draw(img_copy)

    # Obtener configuración de boca
    config = MOUTH_CONFIG.get(character_type)
    if not config:
        return img_copy

    cx = config['center_x']
    cy = config['center_y']

    # Primero, cubrir boca original con un óvalo blanco (área de piel)
    cover_w = 60  # Más grande para cubrir bien
    cover_h = 50
    draw.ellipse([
        cx - cover_w, cy - cover_h,
        cx + cover_w, cy + cover_h
    ], fill='white', outline='white')

    # Dibujar nueva boca según estado
    if mouth_state == 'closed':
        # Línea horizontal
        w = config['closed']['width']
        h = config['closed']['height']
        draw.ellipse([
            cx - w//2, cy - h//2,
            cx + w//2, cy + h//2
        ], fill='black')

    elif mouth_state == 'semi':
        # Óvalo pequeño
        w = config['semi']['width']
        h = config['semi']['height']
        draw.ellipse([
            cx - w//2, cy - h//2,
            cx + w//2, cy + h//2
        ], fill='#8B4513', outline='black', width=3)

    elif mouth_state == 'open':
        # Óvalo grande (boca abierta)
        w = config['open']['width']
        h = config['open']['height']
        draw.ellipse([
            cx - w//2, cy - h//2,
            cx + w//2, cy + h//2
        ], fill='#8B4513', outline='black', width=3)

    return img_copy


def create_animated_character_frame(character_type, mouth_state,
                                    width=600, height=800,
                                    transparent_bg=True,
                                    assets_dir=None):
    """
    Crea frame de personaje PNG con lip sync

    Args:
        character_type: 'mama' o 'papa'
        mouth_state: 'closed', 'semi', 'open'
        width: Ancho del frame
        height: Alto del frame
        transparent_bg: Si usar fondo transparente
        assets_dir: Directorio de assets (opcional)

    Returns:
        PIL.Image: Frame del personaje animado
    """
    if assets_dir is None:
        # Detectar assets_dir automáticamente
        current_dir = Path(__file__).parent.parent.parent
        assets_dir = current_dir / "assets"

    # Cargar personaje base
    character_img = load_character_png(character_type, assets_dir)

    # Animar boca
    character_img = draw_mouth(character_img, character_type, mouth_state)

    # Redimensionar si es necesario
    if character_img.size != (width, height):
        # Mantener aspect ratio
        character_img.thumbnail((width, height), Image.Resampling.LANCZOS)

    # Crear frame con fondo
    if transparent_bg:
        frame = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    else:
        frame = Image.new('RGB', (width, height), (255, 255, 255))

    # Centrar personaje en frame
    x_offset = (width - character_img.width) // 2
    y_offset = (height - character_img.height) // 2

    if transparent_bg:
        frame.paste(character_img, (x_offset, y_offset), character_img)
    else:
        frame.paste(character_img, (x_offset, y_offset))

    return frame


def main():
    """Test del módulo"""
    logger.info("🎨 Test PNG Character Animator")

    # Probar ambos personajes en diferentes estados
    for character in ['mama', 'papa']:
        for state in ['closed', 'semi', 'open']:
            logger.info(f"   Generando {character} - {state}")

            frame = create_animated_character_frame(
                character, state,
                width=600, height=800,
                transparent_bg=True
            )

            # Guardar test
            output_dir = Path(__file__).parent.parent.parent / "output" / "test_png_characters"
            output_dir.mkdir(exist_ok=True, parents=True)

            output_path = output_dir / f"{character}_{state}.png"
            frame.save(output_path)
            logger.info(f"      Guardado: {output_path}")

    logger.info("✅ Test completado")
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
