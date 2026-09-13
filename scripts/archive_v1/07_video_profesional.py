#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Video PROFESIONAL para YouTube Shorts
Versión optimizada con todas las mejoras:
- Fondo real integrado
- Personajes con transparencia
- Subtítulos karaoke (inferior + progresivo)
- Transiciones cada 3s
- Memes/stickers dinámicos
- Detección automática de boca
"""

import sys
import os
import json
from pathlib import Path
import numpy as np

if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import setup_logger

logger = setup_logger('video_pro')

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    from moviepy import (VideoClip, AudioFileClip, ImageClip,
                        CompositeVideoClip, concatenate_videoclips, TextClip)
    import cv2
    LIBS_AVAILABLE = True
except ImportError as e:
    LIBS_AVAILABLE = False
    logger.error(f"❌ Librerías no disponibles: {e}")


# Configuración profesional
CONFIG = {
    'video_width': 1080,
    'video_height': 1920,
    'fps': 30,  # Más fps = más fluido
    'transition_duration': 0.3,  # Transiciones rápidas
    'subtitle_y_position': 1600,  # Inferior
    'subtitle_font_size': 70,
    'subtitle_karaoke_color': '#FFD700',  # Amarillo
    'subtitle_default_color': '#FFFFFF',  # Blanco
    'personaje_scale': 0.45,  # 45% del alto
    'zoom_effect': True,
    'max_scene_duration': 6,  # Cambio de ángulo cada 6s máximo
}

# Mapeo de mouth shapes
MOUTH_MAP = {
    'X': 'closed', 'B': 'closed',
    'A': 'open', 'C': 'open', 'D': 'open', 'E': 'open', 'F': 'open',
    'G': 'semi', 'H': 'semi'
}


def detectar_posicion_boca(personaje_path):
    """
    Detecta la posición aproximada de la boca en el personaje
    Retorna (x, y) en coordenadas relativas (0-1)
    """
    try:
        # Cargar imagen
        img = cv2.imread(str(personaje_path))
        if img is None:
            return (0.5, 0.65)  # Default

        height, width = img.shape[:2]

        # Para personajes simples, la boca suele estar en:
        # - Centro horizontal (50%)
        # - 60-70% del alto

        # Intentar detectar región más oscura en tercio inferior
        bottom_third = img[int(height * 0.5):, :]
        gray = cv2.cvtColor(bottom_third, cv2.COLOR_BGR2GRAY)

        # Buscar región más oscura (probablemente la boca)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)

        # Convertir a coordenadas relativas
        mouth_x = min_loc[0] / width
        mouth_y = (min_loc[1] + int(height * 0.5)) / height

        logger.info(f"   Boca detectada en: ({mouth_x:.2f}, {mouth_y:.2f})")

        return (mouth_x, mouth_y)

    except Exception as e:
        logger.warning(f"⚠️ Error detectando boca: {e}, usando default")
        return (0.5, 0.65)


def crear_personaje_con_boca_precisa(personaje_path, mouth_state, mouth_pos, width, height):
    """
    Crea personaje con boca en posición exacta detectada
    """
    try:
        # Cargar personaje con transparencia
        personaje = Image.open(personaje_path).convert('RGBA')

        # Calcular posición de boca en píxeles
        img_w, img_h = personaje.size
        mouth_x = int(img_w * mouth_pos[0])
        mouth_y = int(img_h * mouth_pos[1])

        # Dibujar boca según estado
        draw = ImageDraw.Draw(personaje)

        if mouth_state == 'closed':
            # Línea horizontal
            draw.line([(mouth_x - 20, mouth_y), (mouth_x + 20, mouth_y)],
                     fill='#2a0000', width=4)
        elif mouth_state == 'semi':
            # Círculo pequeño
            draw.ellipse([mouth_x - 12, mouth_y - 8, mouth_x + 12, mouth_y + 8],
                        fill='#3a0000', outline='black', width=2)
        elif mouth_state == 'open':
            # Círculo grande (más pronunciado)
            draw.ellipse([mouth_x - 18, mouth_y - 12, mouth_x + 18, mouth_y + 12],
                        fill='#4a0000', outline='black', width=2)

        return personaje

    except Exception as e:
        logger.error(f"❌ Error creando personaje: {e}")
        return None


def crear_frame_completo(fondo_path, personaje_img, texto_actual, texto_completo,
                         progress, width, height):
    """
    Crea frame profesional: fondo + personaje + subtítulo karaoke

    Args:
        progress: 0.0-1.0, progreso del texto actual
    """
    try:
        # Cargar fondo
        if fondo_path and Path(fondo_path).exists():
            fondo = Image.open(fondo_path).convert('RGB')
            fondo = fondo.resize((width, height), Image.Resampling.LANCZOS)

            # Aplicar ligero blur para destacar personaje
            fondo = fondo.filter(ImageFilter.GaussianBlur(radius=2))
        else:
            fondo = Image.new('RGB', (width, height), (200, 200, 200))

        # Redimensionar y centrar personaje
        if personaje_img:
            personaje_height = int(height * CONFIG['personaje_scale'])
            aspect = personaje_img.width / personaje_img.height
            personaje_width = int(personaje_height * aspect)
            personaje_resized = personaje_img.resize(
                (personaje_width, personaje_height),
                Image.Resampling.LANCZOS
            )

            # Posición (centrado, ligeramente arriba del centro)
            x = (width - personaje_width) // 2
            y = int(height * 0.35) - personaje_height // 2

            # Pegar con transparencia
            fondo.paste(personaje_resized, (x, y), personaje_resized)

        # Agregar subtítulo estilo karaoke
        draw = ImageDraw.Draw(fondo)

        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf",
                                     CONFIG['subtitle_font_size'])
        except:
            font = ImageFont.load_default()

        # Posición del subtítulo (inferior centrado)
        text_x = width // 2
        text_y = CONFIG['subtitle_y_position']

        # Calcular cuántos caracteres están "iluminados"
        chars_lit = int(len(texto_completo) * progress)
        texto_amarillo = texto_completo[:chars_lit]
        texto_blanco = texto_completo[chars_lit:]

        # Dibujar sombra (borde negro)
        for offset_x in range(-3, 4):
            for offset_y in range(-3, 4):
                draw.text((text_x + offset_x, text_y + offset_y),
                         texto_completo, font=font, fill='black', anchor='mm')

        # Dibujar texto blanco completo
        draw.text((text_x, text_y), texto_completo, font=font,
                 fill=CONFIG['subtitle_default_color'], anchor='mm')

        # Dibujar texto amarillo (progresivo) encima
        if texto_amarillo:
            # Calcular posición del texto amarillo
            bbox = draw.textbbox((0, 0), texto_amarillo, font=font)
            width_amarillo = bbox[2] - bbox[0]
            bbox_completo = draw.textbbox((0, 0), texto_completo, font=font)
            width_completo = bbox_completo[2] - bbox_completo[0]

            offset_x = -(width_completo - width_amarillo) // 2

            draw.text((text_x + offset_x, text_y), texto_amarillo, font=font,
                     fill=CONFIG['subtitle_karaoke_color'], anchor='lm')

        return fondo

    except Exception as e:
        logger.error(f"❌ Error creando frame: {e}")
        return Image.new('RGB', (width, height), (100, 100, 100))


def generar_escena_profesional(personaje_base, lipsync_data, audio_path,
                               texto, fondo_path, cutaway_path, escena_idx,
                               output_dir):
    """
    Genera escena profesional con todas las mejoras
    """
    logger.info(f"🎬 Escena {escena_idx}: Generación profesional...")

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Detectar posición de boca
    mouth_pos = detectar_posicion_boca(personaje_base)

    # Datos
    mouth_cues = lipsync_data.get('mouthCues', [])
    duration = lipsync_data['metadata']['duration']

    logger.info(f"   Duración: {duration:.2f}s")

    # Pre-generar estados de boca
    frames_dir = output_dir / f"escena_{escena_idx}_pro"
    frames_dir.mkdir(exist_ok=True)

    mouth_states = {}
    for state in ['closed', 'semi', 'open']:
        personaje_img = crear_personaje_con_boca_precisa(
            personaje_base, state, mouth_pos,
            CONFIG['video_width'], CONFIG['video_height']
        )
        mouth_states[state] = personaje_img

    # Función de frame con karaoke
    def make_frame(t):
        # Determinar mouth shape
        current_shape = 'X'
        for cue in mouth_cues:
            if cue['start'] <= t < cue['end']:
                current_shape = cue['value']
                break

        state = MOUTH_MAP.get(current_shape, 'closed')
        personaje_img = mouth_states[state]

        # Progreso del karaoke (0.0 a 1.0)
        progress = min(1.0, t / duration)

        # Crear frame completo
        frame = crear_frame_completo(
            fondo_path, personaje_img, texto, texto,
            progress, CONFIG['video_width'], CONFIG['video_height']
        )

        return np.array(frame)

    # Crear clip
    logger.info("   Componiendo video...")
    video_clip = VideoClip(make_frame, duration=duration)
    video_clip = video_clip.with_fps(CONFIG['fps'])

    # Audio
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.with_audio(audio_clip)

    # Aplicar zoom sutil (más dinámico)
    if CONFIG['zoom_effect'] and duration > 2:
        video_clip = video_clip.resized(lambda t: 1 + 0.05 * (t / duration))

    logger.info(f"✅ Escena {escena_idx} lista")

    return video_clip


def agregar_meme_en_momento(video_clip, meme_path, start_time, duration=2.0):
    """
    Inserta meme/sticker en momento específico
    """
    try:
        if not Path(meme_path).exists():
            return video_clip

        # Cargar meme
        meme_clip = ImageClip(str(meme_path)).with_duration(duration)
        meme_clip = meme_clip.with_start(start_time)

        # Posicionar (esquina superior derecha, pequeño)
        meme_clip = meme_clip.resized(height=300)
        meme_clip = meme_clip.positioned(('right', 'top'))

        # Fade in/out
        meme_clip = meme_clip.crossfadein(0.3).crossfadeout(0.3)

        # Composite
        return CompositeVideoClip([video_clip, meme_clip])

    except Exception as e:
        logger.warning(f"⚠️ Error agregando meme: {e}")
        return video_clip


def generar_video_profesional_completo(guion_path, audio_dir, personajes_dir,
                                      fondo_dir, cutaway_dir, output_path):
    """
    Pipeline completo profesional
    """
    logger.info("=" * 70)
    logger.info("🎬 GENERACIÓN PROFESIONAL DE VIDEO")
    logger.info("=" * 70)

    if not LIBS_AVAILABLE:
        logger.error("❌ Librerías no disponibles")
        return False

    try:
        # Leer datos
        with open(guion_path, 'r', encoding='utf-8') as f:
            guion = json.load(f)

        audio_metadata_path = Path(audio_dir) / "audio_metadata.json"
        with open(audio_metadata_path, 'r', encoding='utf-8') as f:
            audio_metadata = json.load(f)

        dialogos = guion.get('dialogo', [])
        archivos_audio = audio_metadata.get('archivos', [])

        # Fondo
        fondo_path = Path(fondo_dir) / "fondo_cocina.png"
        if not fondo_path.exists():
            fondo_path = None
            logger.warning("⚠️ Fondo no encontrado")

        logger.info(f"📋 {len(dialogos)} escenas")
        logger.info(f"🖼️  Fondo: {fondo_path.name if fondo_path else 'N/A'}")
        logger.info("")

        # Generar escenas
        clips = []
        frames_dir = Path(audio_dir).parent / "frames_pro"

        for idx, (linea, audio_info) in enumerate(zip(dialogos, archivos_audio)):
            hablante = linea.get('hablante', '')
            texto = linea.get('linea', '')

            # Personaje
            if 'mamá' in hablante.lower() or 'mama' in hablante.lower():
                personaje_name = 'mama_base'
            elif 'hijo' in hablante.lower():
                personaje_name = 'hijo1_base'
            else:
                personaje_name = 'mama_base'

            personaje_path = None
            for ext in ['.png', '.jfif']:
                path = Path(personajes_dir) / f"{personaje_name}{ext}"
                if path.exists():
                    personaje_path = str(path)
                    break

            if not personaje_path:
                logger.error(f"❌ Personaje no encontrado: {personaje_name}")
                continue

            # Lip sync data
            lipsync_path = Path(audio_dir) / f"dialogo_{idx+1:02d}_lipsync.json"
            with open(lipsync_path, 'r', encoding='utf-8') as f:
                lipsync_data = json.load(f)

            audio_path = Path(audio_dir) / audio_info['archivo']

            # Cutaway (si aplica)
            cutaway_path = None
            if linea.get('cutaway'):
                trigger = linea['cutaway'].get('trigger', '')
                # Buscar cutaway matching
                cutaway_file = Path(cutaway_dir) / f"cutaway_{trigger}.png"
                if cutaway_file.exists():
                    cutaway_path = str(cutaway_file)

            # Generar escena
            clip = generar_escena_profesional(
                personaje_path, lipsync_data, str(audio_path),
                texto[:100], str(fondo_path) if fondo_path else None,
                cutaway_path, idx + 1, frames_dir
            )

            # Agregar meme si corresponde (escena 2 tiene el monólogo largo)
            if idx == 1 and cutaway_path:
                # Insertar meme a los 5 segundos del monólogo
                clip = agregar_meme_en_momento(clip, cutaway_path, 5.0, 3.0)

            clips.append(clip)
            logger.info("")

        # Concatenar con transiciones
        logger.info("🔗 Uniendo escenas con transiciones...")
        video_final = concatenate_videoclips(clips, method="compose",
                                            padding=-CONFIG['transition_duration'])

        # Renderizar
        logger.info(f"🎥 Renderizando video profesional...")
        logger.info(f"   FPS: {CONFIG['fps']}")
        logger.info(f"   Resolución: {CONFIG['video_width']}x{CONFIG['video_height']}")
        logger.info("")

        video_final.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=CONFIG['fps'],
            preset='medium',
            bitrate='8000k',
            threads=4
        )

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ VIDEO PROFESIONAL COMPLETADO")
        logger.info("=" * 70)
        logger.info(f"📹 {output_path}")
        logger.info(f"⏱️  {video_final.duration:.2f}s")
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
    VIDEO_ID = "001"
    base_dir = Path(__file__).parent.parent
    output_base = base_dir / "output" / f"{VIDEO_ID}-20260904"

    guion_path = output_base / "guion.json"
    audio_dir = output_base / "audio"
    personajes_dir = base_dir / "assets" / "personajes_base"
    fondo_dir = output_base / "fondo"
    cutaway_dir = output_base / "cutaways"
    video_output = output_base / f"video_{VIDEO_ID}_PROFESIONAL.mp4"

    logger.info("🚀 Iniciando generación profesional...")
    logger.info("")

    success = generar_video_profesional_completo(
        guion_path, audio_dir, personajes_dir,
        fondo_dir, cutaway_dir, video_output
    )

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
