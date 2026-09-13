#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compositor Profesional
Compone personajes + background con colocación correcta sobre el piso
"""

import sys
import os
from pathlib import Path
import json

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('compositor')

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class SceneCompositor:
    """
    Compositor que coloca personajes sobre el piso del background
    """

    def __init__(self, background_path, output_size=(1080, 1920)):
        """
        Args:
            background_path: Ruta a imagen de fondo
            output_size: Tamaño final (width, height) - formato 9:16
        """
        self.output_size = output_size
        self.bg_path = background_path
        self.background = self._prepare_background(background_path)

        # Detectar línea del piso (con metadata si existe)
        self.floor_y = self._detect_floor_line(background_path)

    def _prepare_background(self, bg_path):
        """
        Prepara el background para composición 9:16
        """
        logger.info(f"📷 Cargando background: {Path(bg_path).name}")

        bg = Image.open(bg_path).convert('RGB')
        original_size = bg.size

        logger.info(f"   Original: {original_size}")

        # Redimensionar para 9:16 manteniendo aspecto
        target_w, target_h = self.output_size

        # Calcular crop para mantener centro
        # Si es 16:9, tomar una porción vertical
        bg_ratio = bg.width / bg.height
        target_ratio = target_w / target_h

        if bg_ratio > target_ratio:
            # Background es más ancho, crop horizontal
            new_height = target_h
            new_width = int(new_height * bg_ratio)
            bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Crop centro
            left = (new_width - target_w) // 2
            bg = bg.crop((left, 0, left + target_w, target_h))
        else:
            # Background es más alto o igual
            new_width = target_w
            new_height = int(new_width / bg_ratio)
            bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Crop centro
            top = (new_height - target_h) // 2
            bg = bg.crop((0, top, target_w, top + target_h))

        logger.info(f"   Final: {bg.size}")

        return bg

    def _detect_floor_line(self, bg_path=None):
        """
        Detecta la línea del piso en el background

        Lee metadata JSON si existe, sino usa aproximación
        """
        # Intentar leer metadata del background
        if bg_path and Path(bg_path).exists():
            metadata_path = Path(bg_path).with_suffix('.json')

            if metadata_path.exists():
                import json
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    if 'floor_position' in metadata:
                        floor_y = int(metadata['floor_position']['y_pixels'])
                        logger.info(f"🏠 Línea del piso (metadata): y={floor_y}")
                        return floor_y
                except Exception as e:
                    logger.warning(f"Error leyendo metadata: {e}")

        # Fallback: aproximación del 75%
        floor_y = int(self.output_size[1] * 0.75)
        logger.warning(f"⚠️  Usando aproximación del piso: y={floor_y}")
        logger.info(f"   💡 Crea {Path(bg_path).with_suffix('.json')} para precisión")

        return floor_y

    def place_character(self, character_img, position='left', scale=0.55):
        """
        Coloca un personaje sobre el piso del escenario

        Args:
            character_img: PIL Image del personaje (con transparencia)
            position: 'left', 'center', 'right'
            scale: Escala del personaje relativo a la altura del escenario

        Returns:
            tuple: (x, y) posición donde colocar el personaje
        """
        # Calcular altura del personaje
        char_height = int(self.output_size[1] * scale)
        char_width = int(char_height * (character_img.width / character_img.height))

        # Redimensionar personaje
        character_resized = character_img.resize(
            (char_width, char_height),
            Image.Resampling.LANCZOS
        )

        # Posición horizontal
        if position == 'left':
            x = int(self.output_size[0] * 0.25) - char_width // 2
        elif position == 'right':
            x = int(self.output_size[0] * 0.75) - char_width // 2
        else:  # center
            x = self.output_size[0] // 2 - char_width // 2

        # Posición vertical: PIES sobre el piso
        y = self.floor_y - char_height

        logger.info(f"   Personaje en posición '{position}': ({x}, {y})")
        logger.info(f"   Tamaño: {char_width}x{char_height}")

        return character_resized, (x, y)

    def compose_scene(self, characters_data, output_path):
        """
        Compone la escena completa

        Args:
            characters_data: Lista de dicts con:
                - image: PIL Image del personaje
                - position: 'left', 'center', 'right'
                - scale: tamaño relativo (opcional)
            output_path: Donde guardar
        """
        logger.info("🎬 Componiendo escena...")

        # Comenzar con background
        scene = self.background.copy()

        # Agregar cada personaje
        for i, char_data in enumerate(characters_data):
            char_img = char_data['image']
            position = char_data.get('position', 'center')
            scale = char_data.get('scale', 0.35)

            # Colocar personaje
            char_resized, (x, y) = self.place_character(char_img, position, scale)

            # Pegar con transparencia
            if char_resized.mode == 'RGBA':
                scene.paste(char_resized, (x, y), char_resized)
            else:
                scene.paste(char_resized, (x, y))

            logger.info(f"   ✅ Personaje {i+1} colocado")

        # Guardar
        scene.save(output_path, quality=95)
        logger.info(f"💾 Escena guardada: {output_path}")

        return scene


def test_compositor():
    """Test del compositor"""
    logger.info("🎬 Test del compositor\n")

    base_dir = Path(__file__).parent.parent.parent

    # Background
    bg_path = base_dir / "output" / "001-20260910" / "backgrounds" / "background_sala_casa.png"

    if not bg_path.exists():
        logger.error(f"❌ Background no encontrado: {bg_path}")
        logger.info("   Esperando generación con Flux...")
        return False

    # Cargar personajes de prueba
    char_dir = base_dir / "output" / "001-20260910" / "test_characters"

    mujer = char_dir / "mujer_expr_disculpa.png"
    hombre = char_dir / "hombre_sumiso_crossed.png"

    if not mujer.exists() or not hombre.exists():
        logger.error("❌ Personajes no encontrados")
        return False

    # Crear compositor
    compositor = SceneCompositor(bg_path)

    # Componer escena
    characters = [
        {
            'image': Image.open(mujer),
            'position': 'left',
            'scale': 0.35
        },
        {
            'image': Image.open(hombre),
            'position': 'right',
            'scale': 0.35
        }
    ]

    output_path = base_dir / "output" / "001-20260910" / "test_composition.png"

    scene = compositor.compose_scene(characters, output_path)

    logger.info(f"\n✅ Composición de prueba lista: {output_path}")
    logger.info("   Los personajes están sobre el piso del escenario")

    return True


if __name__ == '__main__':
    if not PIL_AVAILABLE:
        logger.error("❌ PIL no disponible")
        sys.exit(1)

    success = test_compositor()
    sys.exit(0 if success else 1)
