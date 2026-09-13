#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Generación de Video - MVP (Minimum Viable Product)
Crea video con personajes estáticos + audio + texto
"""

import sys
import os
import json
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger

logger = setup_logger('video_mvp')

try:
    from PIL import Image, ImageDraw, ImageFont
    from moviepy.editor import (ImageClip, AudioFileClip, TextClip,
                                 CompositeVideoClip, concatenate_audioclips,
                                 concatenate_videoclips)
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.error("❌ moviepy o Pillow no instalados")
    logger.info("   Instalar con: pip install moviepy pillow")


def crear_frame_escena(personaje_path, fondo_path, texto, output_path, width=1080, height=1920):
    """
    Crea un frame combinando fondo + personaje + texto

    Args:
        personaje_path: Ruta a PNG del personaje
        fondo_path: Ruta a imagen de fondo
        texto: Texto a superponer
        output_path: Donde guardar el frame
        width, height: Dimensiones del video (9:16 para Shorts)

    Returns:
        str: Ruta al frame generado
    """
    try:
        # Cargar fondo
        if fondo_path and Path(fondo_path).exists():
            fondo = Image.open(fondo_path)
        else:
            # Fondo por defecto (gris)
            fondo = Image.new('RGB', (width, height), color=(200, 200, 200))

        # Redimensionar fondo a 9:16
        fondo = fondo.resize((width, height), Image.Resampling.LANCZOS)

        # Cargar personaje
        if Path(personaje_path).exists():
            personaje = Image.open(personaje_path).convert('RGBA')

            # Redimensionar personaje (50% del alto del video)
            personaje_height = int(height * 0.5)
            aspect = personaje.width / personaje.height
            personaje_width = int(personaje_height * aspect)
            personaje = personaje.resize((personaje_width, personaje_height), Image.Resampling.LANCZOS)

            # Centrar personaje
            x = (width - personaje_width) // 2
            y = (height - personaje_height) // 2

            # Pegar personaje sobre fondo
            fondo.paste(personaje, (x, y), personaje)
        else:
            logger.warning(f"⚠️ Personaje no encontrado: {personaje_path}")

        # Agregar texto (en la parte superior)
        draw = ImageDraw.Draw(fondo)

        # Intentar cargar fuente
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 60)
            except:
                font = ImageFont.load_default()

        # Dibujar texto con borde
        text_x = width // 2
        text_y = 150

        # Borde negro
        for adj in range(-3, 4):
            for adj2 in range(-3, 4):
                draw.text((text_x + adj, text_y + adj2), texto, font=font,
                         fill='black', anchor='mm')

        # Texto blanco
        draw.text((text_x, text_y), texto, font=font, fill='white', anchor='mm')

        # Guardar
        fondo.save(output_path)
        logger.info(f"✅ Frame creado: {Path(output_path).name}")

        return str(output_path)

    except Exception as e:
        logger.error(f"❌ Error creando frame: {e}")
        return None


def generar_video_mvp(guion_path, audio_dir, personajes_dir, output_path):
    """
    Genera video MVP con escenas estáticas + audio

    Args:
        guion_path: Ruta al guion.json
        audio_dir: Carpeta con archivos de audio
        personajes_dir: Carpeta con PNGs de personajes
        output_path: Donde guardar el video final

    Returns:
        bool: True si exitoso
    """
    logger.info("🎬 Generando video MVP...")

    if not MOVIEPY_AVAILABLE:
        logger.error("❌ moviepy no disponible")
        return False

    try:
        # Leer guión
        with open(guion_path, 'r', encoding='utf-8') as f:
            guion = json.load(f)

        # Leer metadata de audio
        audio_metadata_path = Path(audio_dir) / "audio_metadata.json"
        with open(audio_metadata_path, 'r', encoding='utf-8') as f:
            audio_metadata = json.load(f)

        dialogos = guion.get('dialogo', [])
        archivos_audio = audio_metadata.get('archivos', [])

        # Crear frames para cada escena
        clips = []
        frames_dir = Path(audio_dir).parent / "frames"
        frames_dir.mkdir(exist_ok=True)

        for idx, (linea, audio_info) in enumerate(zip(dialogos, archivos_audio)):
            hablante = linea.get('hablante', 'default')
            texto = linea.get('linea', '')[:80]  # Limitar texto

            logger.info(f"🎬 Escena {idx+1}: {hablante}")

            # Determinar qué personaje usar
            if 'mamá' in hablante.lower() or 'mama' in hablante.lower():
                personaje_name = 'mama_base'
            elif 'hijo' in hablante.lower():
                personaje_name = 'hijo1_base'
            else:
                personaje_name = 'mama_base'  # default

            # Buscar PNG del personaje
            personaje_path = None
            for ext in ['.png', '.jfif', '.jpg']:
                path = Path(personajes_dir) / f"{personaje_name}{ext}"
                if path.exists():
                    personaje_path = str(path)
                    break

            if not personaje_path:
                logger.warning(f"⚠️ Personaje no encontrado: {personaje_name}")
                personaje_path = ""

            # Crear frame
            frame_path = frames_dir / f"frame_{idx+1:02d}.png"
            fondo_path = None  # TODO: usar fondo real si existe

            crear_frame_escena(personaje_path, fondo_path, texto, str(frame_path))

            # Cargar audio
            audio_path = Path(audio_dir) / audio_info['archivo']
            audio_clip = AudioFileClip(str(audio_path))

            # Crear clip de video con duración del audio
            image_clip = ImageClip(str(frame_path)).set_duration(audio_clip.duration)
            image_clip = image_clip.set_audio(audio_clip)

            clips.append(image_clip)

            logger.info(f"   Duración: {audio_clip.duration:.2f}s")

        # Concatenar todos los clips
        logger.info(f"🔗 Combinando {len(clips)} escenas...")
        video_final = concatenate_videoclips(clips, method="compose")

        # Configurar FPS
        video_final = video_final.set_fps(24)

        # Renderizar video final
        logger.info(f"🎥 Renderizando video final...")
        logger.info(f"   Output: {output_path}")

        video_final.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=24,
            preset='medium',
            bitrate='8000k'
        )

        logger.info(f"✅ Video generado: {output_path}")
        logger.info(f"   Duración total: {video_final.duration:.2f}s")

        # Limpiar
        video_final.close()
        for clip in clips:
            clip.close()

        return True

    except Exception as e:
        logger.error(f"❌ Error generando video: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Pipeline de generación de video MVP"""
    logger.info("=" * 70)
    logger.info("🎬 GENERACIÓN DE VIDEO - MVP")
    logger.info("=" * 70)

    if not MOVIEPY_AVAILABLE:
        return False

    # Configuración
    VIDEO_ID = "001"
    base_dir = Path(__file__).parent.parent
    output_base = base_dir / "output" / f"{VIDEO_ID}-20260904"

    guion_path = output_base / "guion.json"
    audio_dir = output_base / "audio"
    personajes_dir = base_dir / "assets" / "personajes_base"
    video_output = output_base / f"video_{VIDEO_ID}_mvp.mp4"

    # Verificar que existan los archivos necesarios
    if not guion_path.exists():
        logger.error(f"❌ Guión no encontrado: {guion_path}")
        return False

    if not audio_dir.exists():
        logger.error(f"❌ Carpeta de audio no encontrada: {audio_dir}")
        return False

    logger.info(f"📁 Video: {VIDEO_ID}")
    logger.info(f"📂 Guión: {guion_path}")
    logger.info(f"📂 Audio: {audio_dir}")
    logger.info(f"📂 Personajes: {personajes_dir}")
    logger.info(f"📹 Output: {video_output}")
    logger.info("")

    # Generar video
    success = generar_video_mvp(guion_path, audio_dir, personajes_dir, video_output)

    if success:
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ VIDEO MVP COMPLETADO")
        logger.info("=" * 70)
        logger.info(f"📹 Video disponible en: {video_output}")
        logger.info("")
        logger.info("🎯 Próximos pasos para mejorar:")
        logger.info("   - Agregar fondos reales")
        logger.info("   - Agregar animación con Meta Animated Drawings")
        logger.info("   - Agregar lip sync con Rhubarb")
        logger.info("   - Mejorar transiciones")
        logger.info("=" * 70)

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
