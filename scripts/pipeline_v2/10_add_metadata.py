#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 10: Agregar Metadata Profesional
Agrega metadata que parece de equipo de edición profesional
"""

import sys
import os
from pathlib import Path
import subprocess
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('metadata')


def add_professional_metadata(video_path, output_path=None):
    """
    Agrega metadata profesional al video usando ffmpeg

    Args:
        video_path: Path al video
        output_path: Path del video con metadata (opcional)

    Returns:
        str: Path al video con metadata
    """
    video_path = Path(video_path)

    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_final{video_path.suffix}"

    logger.info("=" * 70)
    logger.info("📝 AGREGANDO METADATA PROFESIONAL")
    logger.info("=" * 70)

    # Metadata profesional (sin nombres de PC ni corporativos)
    metadata = {
        'title': 'Situaciones Cotidianas',
        'artist': 'ElMamon Studios',
        'album': 'Shorts Cómicos',
        'genre': 'Comedy',
        'comment': 'Contenido original de situaciones cotidianas',
        'copyright': f'© {datetime.now().year} ElMamon Studios',
        'encoder': 'Adobe Premiere Pro 2024',  # Parecer profesional
        'creation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    # Construir comando ffmpeg con metadata
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-codec', 'copy',  # No re-encodear (rápido)
        '-map_metadata', '0',  # Preservar metadata existente
    ]

    # Agregar cada campo de metadata
    for key, value in metadata.items():
        cmd.extend(['-metadata', f'{key}={value}'])

    cmd.extend([
        '-y',  # Overwrite
        str(output_path)
    ])

    logger.info(f"📹 Video: {video_path.name}")
    logger.info(f"🎬 Encoder simulado: Adobe Premiere Pro 2024")
    logger.info(f"👨‍💼 Estudio: ElMamon Studios")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ METADATA AGREGADA")
            logger.info("=" * 70)
            logger.info(f"📁 {output_path}")
            return str(output_path)
        else:
            logger.error(f"❌ Error en ffmpeg: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout agregando metadata")
        return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


def main():
    """Agregar metadata al video final"""
    base_dir = Path(__file__).parent.parent.parent

    # Usar directorio de argumentos si se proporciona
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        output_dir = base_dir / "output" / "003-20260912"

    video_path = output_dir / "scene_00s_titled.mp4"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        return False

    result = add_professional_metadata(video_path)

    if result:
        logger.info(f"\n🎉 Video con metadata profesional listo")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
