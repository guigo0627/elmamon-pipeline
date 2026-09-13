#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 7: Video Generator
Genera frames animados y los combina con audio usando MoviePy
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

logger = setup_logger('video_gen')

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("❌ PIL no disponible")

# Import CODE-GENERATED character animator (con diseño final aprobado)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "character_animator",
        Path(__file__).parent / "03_character_animator.py"
    )
    char_animator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(char_animator)
    create_character_frame = char_animator.create_character_frame
    logger.info("✅ Code-generated character_animator importado (diseño final)")
except Exception as e:
    logger.error(f"❌ Error importando character animator: {e}")
    create_character_frame = None

# MoviePy imports (v2.x usa imports directos)
ImageSequenceClip = None
AudioFileClip = None
MOVIEPY_AVAILABLE = False

try:
    from moviepy import ImageSequenceClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
    logger.info("MoviePy disponible")
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    logger.error(f"MoviePy no disponible: {e}")


def detect_floor_from_background(background_path, output_size):
    """
    Detecta la posición del piso desde metadata del background

    Args:
        background_path: Path al background
        output_size: Tamaño del output

    Returns:
        int: Posición Y del piso
    """
    # Buscar archivo JSON con metadata
    bg_path = Path(background_path)
    json_files = list(bg_path.parent.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                import json
                metadata = json.load(f)

            if 'floor_position' in metadata:
                # Usar posición del JSON
                floor_y = int(metadata['floor_position']['y_pixels'])
                # Ajustar a output_size si es diferente
                if output_size[1] != 1920:
                    floor_percentage = metadata['floor_position'].get('percentage', 0.875)
                    floor_y = int(output_size[1] * floor_percentage)
                return floor_y
        except:
            pass

    # Fallback: detección automática simple
    # Para sala_casa: 90% (más abajo para evitar mesas)
    return int(output_size[1] * 0.90)


def generate_animated_frame(frame_num, lip_sync_data, animation_plan, background, background_path, output_size=(1080, 1920)):
    """
    Genera un frame animado con lip sync

    Args:
        frame_num: Número de frame (0-based)
        lip_sync_data: Datos de lip sync
        animation_plan: Plan de animación
        background: PIL Image del background
        output_size: Tamaño del frame

    Returns:
        PIL Image del frame compuesto
    """
    # Obtener mouth state para este frame
    frame_state = lip_sync_data['frame_states'][frame_num]
    mouth_state = frame_state['mouth_state']
    time = frame_state['time']

    # Encontrar escena activa
    scene = None
    for s in animation_plan['scenes']:
        if s['start'] <= time < s['end']:
            scene = s
            break

    if not scene:
        # Usar última escena si estamos fuera de rango
        scene = animation_plan['scenes'][-1]

    # Crear frame base (background)
    frame = background.copy()

    # Detectar piso del background (leer desde metadata si existe)
    floor_y = detect_floor_from_background(background_path, output_size)

    # PARPADEO del personaje que NO habla (patrón natural)
    # Parpadea durante 2-3 frames cada ~50 frames
    blink_cycle = 50  # Parpadea cada 50 frames
    blink_duration = 3  # Dura 3 frames
    char1_blink = False
    char2_blink = False

    # Solo parpadea si NO está hablando
    if mouth_state == 'closed':  # Char1 no habla
        if (frame_num % blink_cycle) < blink_duration:
            char1_blink = True
    else:  # Char1 habla, entonces char2 parpadea
        # Offset para que no parpadeen al mismo tiempo
        if ((frame_num + 25) % blink_cycle) < blink_duration:
            char2_blink = True

    # Posiciones de personajes (75% = 50% más grandes que antes)
    char_height = int(output_size[1] * 0.75)  # Personajes grandes, canvas 1200 evita corte

    # Personaje 1 (speaker - izquierda) - MAMÁ
    char1_data = animation_plan['characters'][0].copy()
    char1_mouth_state = mouth_state if char1_data['speaking'] else 'closed'

    # Crear character_data para personajes code-generated
    char1_data = {'type': 'mama', 'position': 'left'}
    char1_img = create_character_frame(
        char1_data,
        expression='disculpa',  # Expresión según contexto
        gesture='hands_together_apologetic',
        mouth_state=char1_mouth_state,
        width=600,
        height=1200,  # Aumentado para que quepa el cabello completo
        transparent_bg=True,
        blink=char1_blink  # Parpadeo si no está hablando
    )

    # Redimensionar y posicionar
    char1_w = int(char_height * (char1_img.width / char1_img.height))
    char1_img = char1_img.resize((char1_w, char_height), Image.Resampling.LANCZOS)

    # Personajes MÁS JUNTOS para sensación de conversación cercana
    x1 = int(output_size[0] * 0.38) - char1_w // 2
    y1 = floor_y - char_height

    # Pegar personaje 1
    frame.paste(char1_img, (x1, y1), char1_img)

    # Personaje 2 (listener - derecha) - PAPÁ
    char2_data = animation_plan['characters'][1].copy()

    # Crear character_data para personajes code-generated
    char2_data = {'type': 'papa', 'position': 'right'}
    char2_img = create_character_frame(
        char2_data,
        expression='sumiso',  # Expresión según contexto
        gesture='arms_crossed',
        mouth_state='closed',  # No habla
        width=600,
        height=1200,  # Aumentado para que quepa el cabello completo
        transparent_bg=True,
        blink=char2_blink  # Parpadeo mientras escucha
    )

    char2_w = int(char_height * (char2_img.width / char2_img.height))
    char2_img = char2_img.resize((char2_w, char_height), Image.Resampling.LANCZOS)

    # Personajes MÁS JUNTOS
    x2 = int(output_size[0] * 0.62) - char2_w // 2
    y2 = floor_y - char_height

    # Pegar personaje 2
    frame.paste(char2_img, (x2, y2), char2_img)

    return frame


def generate_video_segment(start_frame, end_frame, output_dir, audio_path,
                          lip_sync_data, animation_plan, background_path, fps=30):
    """
    Genera un segmento de video

    Args:
        start_frame: Frame inicial
        end_frame: Frame final
        output_dir: Directorio de salida
        audio_path: Ruta al audio
        lip_sync_data: Datos de lip sync
        animation_plan: Plan de animación
        background_path: Ruta al background
        fps: FPS del video

    Returns:
        str: Ruta al video generado
    """
    output_dir = Path(output_dir)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True, parents=True)

    logger.info(f"🎬 Generando frames {start_frame}-{end_frame}...")

    # Cargar background
    background = Image.open(background_path).convert('RGBA')
    background = background.resize((1080, 1920), Image.Resampling.LANCZOS)

    # Generar frames
    frame_files = []
    for frame_num in range(start_frame, end_frame):
        # Generar frame animado
        frame = generate_animated_frame(
            frame_num, lip_sync_data, animation_plan, background, background_path
        )

        # Guardar frame
        frame_path = frames_dir / f"frame_{frame_num:04d}.png"
        frame.save(frame_path)
        frame_files.append(str(frame_path))

        # Progress
        if (frame_num - start_frame + 1) % 10 == 0:
            progress = ((frame_num - start_frame + 1) / (end_frame - start_frame)) * 100
            logger.info(f"   Progreso: {progress:.1f}% ({frame_num - start_frame + 1}/{end_frame - start_frame} frames)")

    logger.info(f"✅ {len(frame_files)} frames generados")

    # Crear video con MoviePy
    logger.info("🎥 Creando video con audio...")

    clip = ImageSequenceClip(frame_files, fps=fps)

    # Agregar audio (solo el segmento)
    start_time = start_frame / fps
    end_time = end_frame / fps

    audio = AudioFileClip(str(audio_path)).subclipped(start_time, end_time)
    video = clip.with_audio(audio)

    # Guardar
    output_video = output_dir / f"scene_{start_frame//fps:02d}s.mp4"
    video.write_videofile(
        str(output_video),
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        fps=fps
    )

    logger.info(f"✅ Video generado: {output_video}")

    return str(output_video)


def main():
    """Generar video COMPLETO (todos los frames)"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "output" / "003-20260912"

    # Cargar datos
    with open(output_dir / "lip_sync_data.json", 'r', encoding='utf-8') as f:
        lip_sync_data = json.load(f)

    with open(output_dir / "animation_plan.json", 'r', encoding='utf-8') as f:
        animation_plan = json.load(f)

    audio_path = output_dir / "audio_original.mpeg"
    background_path = output_dir / "backgrounds" / "background_sala_casa.png"

    logger.info("=" * 70)
    logger.info("🎬 GENERACIÓN DE VIDEO COMPLETO")
    logger.info("=" * 70)
    logger.info(f"⏱️  Duración: {lip_sync_data['duration']:.2f}s")
    logger.info(f"🎬 Frames totales: {lip_sync_data['total_frames']}")

    # Generar video completo (todos los frames)
    start_frame = 0
    end_frame = lip_sync_data['total_frames']

    video_path = generate_video_segment(
        start_frame, end_frame,
        output_dir, audio_path,
        lip_sync_data, animation_plan,
        background_path, fps=30
    )

    logger.info("")
    logger.info("=" * 70)
    logger.info("🎉 VIDEO COMPLETO GENERADO")
    logger.info("=" * 70)
    logger.info(f"📁 {video_path}")
    logger.info(f"⏱️  Duración: {lip_sync_data['duration']:.2f}s")
    logger.info(f"🎬 Frames: {lip_sync_data['total_frames']}")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
