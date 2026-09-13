#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Imágenes para Redes Sociales
Genera logo y banner usando nuestros personajes
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

# Importar módulo de personajes
import importlib.util
spec = importlib.util.spec_from_file_location(
    "character_animator",
    Path(__file__).parent.parent / "pipeline_v2" / "03_character_animator.py"
)
char_animator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(char_animator)

logger = setup_logger('branding')


def generate_logo(output_path, size=(320, 320)):
    """
    Genera logo para perfil de Facebook

    Args:
        output_path: Path donde guardar el logo
        size: Tamaño del logo (320x320)
    """
    logger.info("🎨 Generando logo...")

    # Crear canvas con fondo azul vibrante
    img = Image.new('RGB', size, '#2E5EFF')  # Azul Facebook-style
    draw = ImageDraw.Draw(img)

    # Generar personajes pequeños (lado a lado)
    char_size = int(size[0] * 0.35)  # 35% del ancho cada uno

    # Mamá (izquierda)
    mama_data = {'type': 'mama', 'position': 'left'}
    mama_img = char_animator.create_character_frame(
        mama_data,
        expression='disculpa',
        gesture='hands_together_apologetic',
        mouth_state='semi',
        width=char_size,
        height=int(char_size * 1.5),
        transparent_bg=True
    )

    # Papá (derecha)
    papa_data = {'type': 'papa', 'position': 'right'}
    papa_img = char_animator.create_character_frame(
        papa_data,
        expression='sumiso',
        gesture='arms_crossed',
        mouth_state='closed',
        width=char_size,
        height=int(char_size * 1.5),
        transparent_bg=True
    )

    # Posicionar personajes (abajo del logo)
    mama_x = int(size[0] * 0.15)
    papa_x = int(size[0] * 0.55)
    char_y = int(size[1] * 0.35)

    # Redimensionar para que quepan
    mama_img = mama_img.resize((char_size, int(char_size * 1.5)), Image.Resampling.LANCZOS)
    papa_img = papa_img.resize((char_size, int(char_size * 1.5)), Image.Resampling.LANCZOS)

    img.paste(mama_img, (mama_x, char_y), mama_img)
    img.paste(papa_img, (papa_x, char_y), papa_img)

    # Texto "ElMamón" arriba
    try:
        # Intentar usar fuente Arial Bold
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
    except:
        # Fallback a fuente default
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

    # Título
    title = "ElMamón"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox[2] - bbox[0]
    text_x = (size[0] - text_width) // 2
    text_y = int(size[1] * 0.08)

    # Sombra
    draw.text((text_x + 2, text_y + 2), title, font=font_title, fill='#000000')
    # Texto principal
    draw.text((text_x, text_y), title, font=font_title, fill='#FFFFFF')

    # Subtítulo
    subtitle = "Situaciones Cotidianas"
    bbox_sub = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_width = bbox_sub[2] - bbox_sub[0]
    sub_x = (size[0] - sub_width) // 2
    sub_y = text_y + 55

    draw.text((sub_x, sub_y), subtitle, font=font_subtitle, fill='#FFFFFF')

    # Guardar
    img.save(output_path, quality=95)
    logger.info(f"✅ Logo guardado: {output_path}")

    return str(output_path)


def generate_banner(output_path, size=(820, 312)):
    """
    Genera banner/portada para Facebook

    Args:
        output_path: Path donde guardar el banner
        size: Tamaño del banner (820x312)
    """
    logger.info("🖼️  Generando banner...")

    # Crear canvas con gradiente
    img = Image.new('RGB', size, '#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Fondo degradado azul a morado
    for i in range(size[1]):
        # Gradiente de azul (#2E5EFF) a morado (#9D4EFF)
        r = int(46 + (157 - 46) * (i / size[1]))
        g = int(94 + (78 - 94) * (i / size[1]))
        b = 255
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))

    # Generar personajes más grandes
    char_width = int(size[0] * 0.20)  # 20% del ancho cada uno
    char_height = int(size[1] * 0.85)  # 85% de la altura

    # Mamá (izquierda) - expresión cómica
    mama_data = {'type': 'mama', 'position': 'left'}
    mama_img = char_animator.create_character_frame(
        mama_data,
        expression='disculpa',
        gesture='hands_together_apologetic',
        mouth_state='open',  # Hablando
        width=int(char_width * 1.2),
        height=int(char_height * 1.5),
        transparent_bg=True
    )

    # Papá (derecha) - expresión sumisa
    papa_data = {'type': 'papa', 'position': 'right'}
    papa_img = char_animator.create_character_frame(
        papa_data,
        expression='sumiso',
        gesture='arms_crossed',
        mouth_state='closed',
        width=int(char_width * 1.2),
        height=int(char_height * 1.5),
        transparent_bg=True
    )

    # Redimensionar para banner
    mama_img = mama_img.resize((char_width, char_height), Image.Resampling.LANCZOS)
    papa_img = papa_img.resize((char_width, char_height), Image.Resampling.LANCZOS)

    # Posicionar
    mama_x = int(size[0] * 0.08)  # 8% desde la izquierda
    papa_x = int(size[0] * 0.72)  # 72% desde la izquierda
    char_y = int(size[1] * 0.12)  # 12% desde arriba

    img.paste(mama_img, (mama_x, char_y), mama_img)
    img.paste(papa_img, (papa_x, char_y), papa_img)

    # Texto central
    try:
        font_main = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 64)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        font_cta = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_cta = ImageFont.load_default()

    # Título principal (centro)
    title = "Situaciones"
    title2 = "Cotidianas"

    # Primera línea
    bbox1 = draw.textbbox((0, 0), title, font=font_main)
    width1 = bbox1[2] - bbox1[0]
    x1 = (size[0] - width1) // 2
    y1 = int(size[1] * 0.25)

    # Sombra
    draw.text((x1 + 3, y1 + 3), title, font=font_main, fill='#000000')
    draw.text((x1, y1), title, font=font_main, fill='#FFFFFF')

    # Segunda línea
    bbox2 = draw.textbbox((0, 0), title2, font=font_main)
    width2 = bbox2[2] - bbox2[0]
    x2 = (size[0] - width2) // 2
    y2 = y1 + 70

    draw.text((x2 + 3, y2 + 3), title2, font=font_main, fill='#000000')
    draw.text((x2, y2), title2, font=font_main, fill='#FFFFFF')

    # Subtítulo
    subtitle = "Videos cómicos de la vida real 😂"
    bbox_sub = draw.textbbox((0, 0), subtitle, font=font_sub)
    sub_width = bbox_sub[2] - bbox_sub[0]
    sub_x = (size[0] - sub_width) // 2
    sub_y = y2 + 80

    draw.text((sub_x + 2, sub_y + 2), subtitle, font=font_sub, fill='#000000')
    draw.text((sub_x, sub_y), subtitle, font=font_sub, fill='#FFD700')  # Dorado

    # Call to action
    cta = "¡SÍGUENOS! 👉"
    bbox_cta = draw.textbbox((0, 0), cta, font=font_cta)
    cta_width = bbox_cta[2] - bbox_cta[0]
    cta_x = (size[0] - cta_width) // 2
    cta_y = sub_y + 45

    # Fondo del CTA (rectángulo)
    padding = 10
    draw.rectangle([
        cta_x - padding, cta_y - 5,
        cta_x + cta_width + padding, cta_y + 30
    ], fill='#FF6B35', outline='#FFFFFF', width=2)

    draw.text((cta_x, cta_y), cta, font=font_cta, fill='#FFFFFF')

    # Guardar
    img.save(output_path, quality=95)
    logger.info(f"✅ Banner guardado: {output_path}")

    return str(output_path)


def main():
    """Generar todas las imágenes de branding"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "assets" / "branding"
    output_dir.mkdir(exist_ok=True, parents=True)

    logger.info("=" * 70)
    logger.info("🎨 GENERANDO IMÁGENES DE BRANDING")
    logger.info("=" * 70)

    # Logo
    logo_path = output_dir / "logo_facebook_320x320.png"
    generate_logo(logo_path)

    # Banner
    banner_path = output_dir / "banner_facebook_820x312.png"
    generate_banner(banner_path)

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ BRANDING COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"📁 {output_dir}")
    logger.info(f"   - logo_facebook_320x320.png")
    logger.info(f"   - banner_facebook_820x312.png")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
