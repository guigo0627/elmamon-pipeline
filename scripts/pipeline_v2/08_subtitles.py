#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 8: Subtítulos Karaoke
Agrega subtítulos progresivos estilo karaoke al video
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

logger = setup_logger('subtitles')

try:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.error("MoviePy no disponible")


def create_karaoke_subtitle(text, start_time, duration, video_size=(1080, 1920)):
    """
    Crea un subtítulo estilo karaoke

    Args:
        text: Texto a mostrar
        start_time: Tiempo de inicio (segundos)
        duration: Duración (segundos)
        video_size: Tamaño del video (width, height)

    Returns:
        TextClip configurado
    """
    # Configuración del subtítulo
    subtitle = TextClip(
        text=text,
        font_size=60,
        color='yellow',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(video_size[0] - 100, None),  # Márgenes laterales
        align='center'
    )

    # Posicionar en parte inferior (10% desde abajo)
    subtitle = subtitle.with_position(('center', video_size[1] - 200))

    # Timing
    subtitle = subtitle.with_start(start_time).with_duration(duration)

    return subtitle


def add_subtitles_to_video(video_path, transcription_path, output_path):
    """
    Agrega subtítulos al video

    Args:
        video_path: Ruta al video sin subtítulos
        transcription_path: Ruta a transcription.json
        output_path: Donde guardar el video con subtítulos

    Returns:
        str: Ruta al video con subtítulos
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy no disponible")
        return None

    logger.info("=" * 70)
    logger.info("📝 AGREGANDO SUBTÍTULOS KARAOKE")
    logger.info("=" * 70)

    # Cargar video
    video = VideoFileClip(str(video_path))

    # Cargar transcripción
    with open(transcription_path, 'r', encoding='utf-8') as f:
        transcription = json.load(f)

    # Generar subtítulos por palabra (estilo karaoke)
    subtitles = []

    for word_data in transcription.get('words', []):
        text = word_data['text']
        start = word_data['start'] / 1000  # ms a segundos
        end = word_data['end'] / 1000
        duration = end - start

        # Crear subtítulo para esta palabra
        subtitle = create_karaoke_subtitle(
            text, start, duration,
            video_size=(video.w, video.h)
        )

        subtitles.append(subtitle)

    logger.info(f"📝 {len(subtitles)} palabras para subtitular")

    # Componer video con subtítulos
    logger.info("🎬 Componiendo video...")

    final_video = CompositeVideoClip([video] + subtitles)

    # Guardar
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
    logger.info("✅ SUBTÍTULOS AGREGADOS")
    logger.info("=" * 70)

    return str(output_path)


def main():
    """Test del módulo de subtítulos"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "output" / "001-20260910"

    video_path = output_dir / "scene_00s.mp4"
    transcription_path = output_dir / "transcription.json"
    output_path = output_dir / "scene_00s_subtitled.mp4"

    if not video_path.exists():
        logger.error(f"Video no encontrado: {video_path}")
        return False

    if not transcription_path.exists():
        logger.error(f"Transcripción no encontrada: {transcription_path}")
        return False

    result = add_subtitles_to_video(
        video_path, transcription_path, output_path
    )

    if result:
        logger.info(f"\n🎉 Video con subtítulos: {result}")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
