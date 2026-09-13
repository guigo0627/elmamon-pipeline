#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Video con Lip Sync Visual
Crea video profesional con sincronización labial basada en datos de Rhubarb
"""

import sys
import os
import json
from pathlib import Path
import numpy as np

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import setup_logger

logger = setup_logger('video_lipsync')

try:
    from PIL import Image, ImageDraw, ImageFont
    from moviepy import VideoClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("❌ PIL/moviepy no disponibles")


# Mapeo de mouth shapes de Rhubarb a estados simples
MOUTH_SHAPE_MAP = {
    'X': 'closed',    # Silencio
    'A': 'open',      # Vocal abierta
    'B': 'closed',    # Labios cerrados
    'C': 'open',      # Consonante
    'D': 'open',      # Dental
    'E': 'open',      # Eh
    'F': 'open',      # Labio-dental
    'G': 'semi',      # Gutural
    'H': 'semi'       # Aspirada
}


def crear_personaje_con_boca(personaje_base_path, mouth_state, output_path, width=1080, height=1920):
    """
    Crea versión del personaje con boca en estado específico

    Args:
        personaje_base_path: Ruta al PNG base del personaje
        mouth_state: 'closed', 'semi', 'open'
        output_path: Donde guardar
        width, height: Dimensiones finales

    Returns:
        str: Ruta al archivo generado
    """
    try:
        # Cargar personaje
        personaje = Image.open(personaje_base_path).convert('RGBA')

        # Por ahora, simplemente superponer un círculo negro/rojo según estado
        # En una versión más elaborada, se cargarían imágenes de boca pre-dibujadas

        draw = ImageDraw.Draw(personaje)

        # Posición aproximada de la boca (centro-inferior del personaje)
        img_w, img_h = personaje.size
        mouth_x = img_w // 2
        mouth_y = int(img_h * 0.65)

        # Dibujar boca según estado
        if mouth_state == 'closed':
            # Línea horizontal
            draw.line([(mouth_x - 30, mouth_y), (mouth_x + 30, mouth_y)],
                     fill='black', width=5)
        elif mouth_state == 'semi':
            # Círculo pequeño
            draw.ellipse([mouth_x - 15, mouth_y - 10, mouth_x + 15, mouth_y + 10],
                        fill='#4a0000', outline='black', width=3)
        elif mouth_state == 'open':
            # Círculo grande
            draw.ellipse([mouth_x - 25, mouth_y - 15, mouth_x + 25, mouth_y + 15],
                        fill='#4a0000', outline='black', width=3)

        # Crear canvas final
        canvas = Image.new('RGBA', (width, height), (240, 240, 240, 255))

        # Redimensionar y centrar personaje
        personaje_height = int(height * 0.5)
        aspect = personaje.width / personaje.height
        personaje_width = int(personaje_height * aspect)
        personaje = personaje.resize((personaje_width, personaje_height), Image.Resampling.LANCZOS)

        x = (width - personaje_width) // 2
        y = (height - personaje_height) // 2

        canvas.paste(personaje, (x, y), personaje)

        # Guardar
        canvas.save(output_path)
        return str(output_path)

    except Exception as e:
        logger.error(f"❌ Error creando personaje: {e}")
        return None


def crear_frame_con_texto(personaje_path, texto, output_path, width=1080, height=1920):
    """
    Agrega texto sobre el frame del personaje
    """
    try:
        # Cargar imagen base
        img = Image.open(personaje_path).convert('RGB')
        draw = ImageDraw.Draw(img)

        # Fuente
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 50)
        except:
            font = ImageFont.load_default()

        # Posición del texto (arriba, centrado)
        text_x = width // 2
        text_y = 150

        # Borde negro
        for adj_x in range(-2, 3):
            for adj_y in range(-2, 3):
                draw.text((text_x + adj_x, text_y + adj_y), texto,
                         font=font, fill='black', anchor='mm')

        # Texto blanco
        draw.text((text_x, text_y), texto, font=font, fill='white', anchor='mm')

        img.save(output_path)
        return str(output_path)

    except Exception as e:
        logger.error(f"❌ Error agregando texto: {e}")
        return None


def generar_video_escena(personaje_base, lipsync_data, audio_path, texto, output_dir, escena_idx):
    """
    Genera video de una escena con lip sync

    Args:
        personaje_base: Ruta al PNG base del personaje
        lipsync_data: Dict con datos de Rhubarb
        audio_path: Ruta al audio
        texto: Texto a mostrar
        output_dir: Directorio de salida
        escena_idx: Índice de la escena

    Returns:
        VideoClip: Clip de video generado
    """
    logger.info(f"🎬 Generando escena {escena_idx}...")

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Obtener mouth cues
    mouth_cues = lipsync_data.get('mouthCues', [])
    duration = lipsync_data['metadata']['duration']

    logger.info(f"   Duración: {duration:.2f}s, {len(mouth_cues)} mouth cues")

    # Generar frames con diferentes bocas
    frames_dir = output_dir / f"escena_{escena_idx}_frames"
    frames_dir.mkdir(exist_ok=True)

    # Pre-generar personajes con cada estado de boca
    logger.info("   Generando estados de boca...")
    mouth_states = {}
    for state in ['closed', 'semi', 'open']:
        state_path = frames_dir / f"personaje_{state}.png"
        crear_personaje_con_boca(personaje_base, state, state_path)

        # Agregar texto
        final_path = frames_dir / f"frame_{state}.png"
        crear_frame_con_texto(state_path, texto[:60], final_path)
        mouth_states[state] = str(final_path)

    logger.info("   Estados de boca listos")

    # Crear función que retorna el frame correcto según el tiempo
    def make_frame(t):
        """Retorna el frame apropiado para el tiempo t"""
        # Buscar el mouth cue correspondiente
        current_shape = 'X'  # default: cerrado

        for cue in mouth_cues:
            if cue['start'] <= t < cue['end']:
                current_shape = cue['value']
                break

        # Mapear a estado
        state = MOUTH_SHAPE_MAP.get(current_shape, 'closed')

        # Cargar imagen
        img_path = mouth_states[state]
        img = Image.open(img_path)
        return np.array(img)

    # Crear video clip
    logger.info("   Creando video clip...")
    video_clip = VideoClip(make_frame, duration=duration)
    video_clip = video_clip.with_fps(24)

    # Agregar audio
    logger.info("   Agregando audio...")
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.with_audio(audio_clip)

    logger.info(f"✅ Escena {escena_idx} generada")

    return video_clip


def generar_video_completo(guion_path, audio_dir, personajes_dir, output_path):
    """
    Genera video completo con todas las escenas
    """
    logger.info("=" * 70)
    logger.info("🎬 GENERANDO VIDEO CON LIP SYNC")
    logger.info("=" * 70)

    if not PIL_AVAILABLE:
        logger.error("❌ Dependencias no disponibles")
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

        logger.info(f"📋 {len(dialogos)} escenas a generar")
        logger.info("")

        # Generar cada escena
        clips = []
        frames_base_dir = Path(audio_dir).parent / "frames_lipsync"

        for idx, (linea, audio_info) in enumerate(zip(dialogos, archivos_audio)):
            hablante = linea.get('hablante', 'default')
            texto = linea.get('linea', '')

            # Determinar personaje
            if 'mamá' in hablante.lower() or 'mama' in hablante.lower():
                personaje_name = 'mama_base'
            elif 'hijo' in hablante.lower():
                personaje_name = 'hijo1_base'
            else:
                personaje_name = 'mama_base'

            # Buscar PNG
            personaje_path = None
            for ext in ['.png', '.jfif']:
                path = Path(personajes_dir) / f"{personaje_name}{ext}"
                if path.exists():
                    personaje_path = str(path)
                    break

            if not personaje_path:
                logger.error(f"❌ Personaje no encontrado: {personaje_name}")
                continue

            # Cargar datos de lip sync
            lipsync_path = Path(audio_dir) / f"dialogo_{idx+1:02d}_lipsync.json"
            with open(lipsync_path, 'r', encoding='utf-8') as f:
                lipsync_data = json.load(f)

            # Audio
            audio_path = Path(audio_dir) / audio_info['archivo']

            # Generar escena
            clip = generar_video_escena(
                personaje_path,
                lipsync_data,
                str(audio_path),
                texto,
                frames_base_dir,
                idx + 1
            )

            clips.append(clip)
            logger.info("")

        # Concatenar clips
        logger.info("🔗 Combinando todas las escenas...")
        video_final = concatenate_videoclips(clips, method="compose")

        # Renderizar
        logger.info(f"🎥 Renderizando video final...")
        logger.info(f"   Output: {output_path}")
        logger.info(f"   Duración total: {video_final.duration:.2f}s")
        logger.info("")

        video_final.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=24,
            preset='fast',
            bitrate='6000k',
            threads=4
        )

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ VIDEO COMPLETADO CON ÉXITO")
        logger.info("=" * 70)
        logger.info(f"📹 {output_path}")
        logger.info(f"⏱️  Duración: {video_final.duration:.2f}s")
        logger.info("=" * 70)

        # Limpiar
        video_final.close()
        for clip in clips:
            clip.close()

        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Pipeline principal"""
    logger.info("🎬 INICIANDO GENERACIÓN DE VIDEO")

    # Configuración
    VIDEO_ID = "001"
    base_dir = Path(__file__).parent.parent
    output_base = base_dir / "output" / f"{VIDEO_ID}-20260904"

    guion_path = output_base / "guion.json"
    audio_dir = output_base / "audio"
    personajes_dir = base_dir / "assets" / "personajes_base"
    video_output = output_base / f"video_{VIDEO_ID}_con_lipsync.mp4"

    if not guion_path.exists():
        logger.error(f"❌ Guión no encontrado: {guion_path}")
        return False

    if not audio_dir.exists():
        logger.error(f"❌ Audio no encontrado: {audio_dir}")
        return False

    logger.info(f"📁 Guión: {guion_path}")
    logger.info(f"📁 Audio: {audio_dir}")
    logger.info(f"📁 Personajes: {personajes_dir}")
    logger.info(f"📹 Output: {video_output}")
    logger.info("")

    success = generar_video_completo(guion_path, audio_dir, personajes_dir, video_output)

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
