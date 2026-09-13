#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 9: Título Estático Gancho
Agrega título estático tipo meme/gancho en la parte superior del video
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

logger = setup_logger('title')

try:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


def create_static_title(text, video_duration, video_size=(1080, 1920)):
    """
    Crea un título estático para el video

    Args:
        text: Texto del título
        video_duration: Duración del video (segundos)
        video_size: Tamaño del video (width, height)

    Returns:
        TextClip configurado
    """
    # Configuración del título (parte superior)
    # Usar Arial Bold con path completo (Windows) para UTF-8
    # Ajustado para área segura de Facebook Reels (15% desde arriba)
    title = TextClip(
        text=text,
        font='C:/Windows/Fonts/arialbd.ttf',  # Arial Bold con soporte UTF-8
        font_size=65,  # Reducido de 70 a 65 para mejor ajuste
        color='white',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(video_size[0] - 100, None)  # Márgenes 50px cada lado
    )

    # Posicionar en área segura de Facebook (15% desde arriba)
    title = title.with_position(('center', int(video_size[1] * 0.15)))

    # Duración completa del video
    title = title.with_duration(video_duration)

    return title


def add_title_to_video(video_path, animation_plan_path, output_path=None):
    """
    Agrega título estático al video

    Args:
        video_path: Path al video sin título
        animation_plan_path: Path a animation_plan.json
        output_path: Path del video con título (opcional)

    Returns:
        str: Path al video con título o None si falla
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("❌ MoviePy no disponible")
        return None

    logger.info("=" * 70)
    logger.info("🏷️  AGREGANDO TÍTULO GANCHO")
    logger.info("=" * 70)

    # Cargar video
    video = VideoFileClip(str(video_path))

    # Cargar animation plan
    with open(animation_plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    # Obtener título (asegurando UTF-8)
    title_text = plan['analysis'].get('recommended_title', '')

    if not title_text:
        # Fallback: usar primer título de la lista
        title_text = plan['analysis'].get('hook_titles', [''])[0]

    if not title_text:
        logger.error("❌ No hay título en animation_plan.json")
        return None

    # Asegurar encoding correcto
    if isinstance(title_text, bytes):
        title_text = title_text.decode('utf-8')

    logger.info(f"🏷️  Título: {title_text}")

    # Crear título
    title_clip = create_static_title(
        title_text,
        video.duration,
        (video.w, video.h)
    )

    # Componer video con título
    logger.info("🎬 Componiendo...")

    final_video = CompositeVideoClip([video, title_clip])

    # Guardar
    if output_path is None:
        output_path = Path(str(video_path).replace('.mp4', '_titled.mp4'))

    logger.info(f"💾 Guardando: {output_path}")

    final_video.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        fps=video.fps,
        logger=None
    )

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ TÍTULO AGREGADO")
    logger.info("=" * 70)

    return str(output_path)


def main():
    """Test del módulo"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "output" / "003-20260912"

    video_path = output_dir / "scene_00s.mp4"
    animation_plan_path = output_dir / "animation_plan.json"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        return False

    if not animation_plan_path.exists():
        logger.error(f"❌ Animation plan no encontrado: {animation_plan_path}")
        return False

    result = add_title_to_video(video_path, animation_plan_path)

    if result:
        logger.info(f"\n🎉 Video con título: {result}")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
