#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 7 FAMILY: Video Generator con 3+ Personajes
Genera frames con múltiples personajes en escena (familia)
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

logger = setup_logger('video_gen_family')

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("❌ PIL no disponible")

# Import character animator
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "character_animator",
        Path(__file__).parent / "03_character_animator.py"
    )
    char_animator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(char_animator)
    create_character_frame = char_animator.create_character_frame
    logger.info("✅ Character animator importado")
except Exception as e:
    logger.error(f"❌ Error importando character animator: {e}")
    create_character_frame = None

# MoviePy imports
try:
    from moviepy import ImageSequenceClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.error("❌ MoviePy no disponible")


def get_zoom_effect(frame_num, camera_effects):
    """
    Determina el zoom actual según camera_effects

    Returns:
        dict: {'target': 'mama'/'hijo1'/'hijo2', 'zoom_level': 1.0-2.0}
    """
    if not camera_effects:
        return {'target': 'all', 'zoom_level': 1.0}

    for effect in camera_effects:
        if effect.get('type') == 'zoom':
            start = effect.get('start_frame', 0)
            end = effect.get('end_frame', 999999)

            if start <= frame_num < end:
                return {
                    'target': effect.get('target', 'all'),
                    'zoom_level': 1.5  # Zoom moderado
                }

    return {'target': 'all', 'zoom_level': 1.0}


def generate_frame_family(
    frame_num,
    lip_sync_data,
    animation_plan,
    background,
    output_size=(1080, 1920)
):
    """
    Genera un frame con múltiples personajes (familia)

    Args:
        frame_num: Número de frame
        lip_sync_data: Datos de lip sync
        animation_plan: Plan de animación con personajes
        background: Background image
        output_size: Tamaño del output

    Returns:
        PIL Image del frame
    """
    # Copiar background
    frame = background.copy()

    # Obtener mouth state del frame
    frame_state = lip_sync_data['frame_states'][frame_num]
    mouth_state = frame_state['mouth_state']

    # Parpadeo natural (cíclico)
    blink_cycle = 50
    blink_duration = 3
    blink = (frame_num % blink_cycle) < blink_duration

    # Obtener personajes del animation plan
    characters = animation_plan.get('characters', [])

    # Obtener zoom effect
    camera_effects = animation_plan.get('camera_effects', [])
    zoom_effect = get_zoom_effect(frame_num, camera_effects)

    # Floor position
    floor_y = int(output_size[1] * 0.90)

    # Generar cada personaje
    character_images = []

    for i, char_data in enumerate(characters):
        char_type = char_data.get('type', 'papa')
        char_name = char_data.get('name', f'character_{i}')
        position = char_data.get('position', 'center')
        speaking = char_data.get('speaking', False)
        expression = char_data.get('expression', 'neutral')
        gesture = char_data.get('gesture', 'idle')

        # Determinar mouth state para este personaje
        if speaking:
            char_mouth_state = mouth_state  # Usa lip sync real
        else:
            char_mouth_state = 'closed'  # Siempre cerrado

        # Determinar si parpadea
        char_blink = blink  # Todos parpadean igual

        # Tamaño del personaje (FIJO - sin zoom que cambie tamaño)
        # Mamá más grande, hijos más pequeños
        if char_type == 'mama':
            char_height = int(output_size[1] * 0.65)  # Mamá grande
        else:
            char_height = int(output_size[1] * 0.50)  # Hijos más pequeños

        # Zoom solo para efecto visual (no cambia tamaño)
        char_target_id = char_name.lower().replace(' ', '')
        is_zoomed = (zoom_effect['target'] == char_target_id or zoom_effect['target'] == 'all')

        # Generar personaje
        char_img = create_character_frame(
            char_data,
            expression=expression,
            gesture=gesture,
            mouth_state=char_mouth_state,
            width=int(char_height * 0.5),
            height=char_height,
            transparent_bg=True,
            blink=char_blink
        )

        # Calcular posición según layout (MÁS SEPARADOS)
        char_w = int(char_height * (char_img.width / char_img.height))

        if position == 'center':
            x = (output_size[0] - char_w) // 2
        elif position == 'left':
            x = int(output_size[0] * 0.05)  # Más a la izquierda (antes 0.15)
        elif position == 'right':
            x = int(output_size[0] * 0.95) - char_w  # Más a la derecha (antes 0.85)
        else:
            x = (output_size[0] - char_w) // 2

        # Y position FIJA (no cambia con zoom)
        y = floor_y - char_height

        character_images.append({
            'image': char_img,
            'position': (x, y),
            'zoomed': is_zoomed
        })

    # Pegar personajes en el frame (primero los no-zoomed, luego los zoomed)
    for char_data in sorted(character_images, key=lambda x: x['zoomed']):
        frame.paste(char_data['image'], char_data['position'], char_data['image'])

    return frame


def generate_video_family(
    output_dir,
    lip_sync_data,
    animation_plan,
    background_path=None,
    fps=30
):
    """
    Genera video completo con múltiples personajes (familia)

    Args:
        output_dir: Directorio de salida
        lip_sync_data: Datos de lip sync
        animation_plan: Plan de animación
        background_path: Path al background (o None para color sólido)
        fps: FPS del video

    Returns:
        str: Path al video generado
    """
    output_dir = Path(output_dir)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True, parents=True)

    output_size = (1080, 1920)

    logger.info("=" * 70)
    logger.info("🎬 GENERANDO VIDEO CON MÚLTIPLES PERSONAJES")
    logger.info("=" * 70)

    # Cargar o crear background
    if background_path and Path(background_path).exists():
        background = Image.open(background_path).convert('RGB')
        background = background.resize(output_size, Image.Resampling.LANCZOS)
        logger.info(f"✅ Background cargado: {Path(background_path).name}")
    else:
        # Crear background color sólido (beige claro)
        background = Image.new('RGB', output_size, (245, 235, 220))
        logger.info("🎨 Background: Color sólido beige")

    # Generar frames
    total_frames = len(lip_sync_data['frame_states'])
    logger.info(f"📊 Generando {total_frames} frames...")

    frame_files = []
    for frame_num in range(total_frames):
        if frame_num % 50 == 0:
            logger.info(f"  Frame {frame_num}/{total_frames} ({frame_num*100//total_frames}%)")

        frame = generate_frame_family(
            frame_num,
            lip_sync_data,
            animation_plan,
            background,
            output_size
        )

        frame_path = frames_dir / f"frame_{frame_num:04d}.png"
        frame.save(frame_path)
        frame_files.append(str(frame_path))

    logger.info("✅ Todos los frames generados")

    # Componer video con MoviePy
    if not MOVIEPY_AVAILABLE:
        logger.error("❌ MoviePy no disponible, no se puede generar video")
        return None

    logger.info("🎞️  Componiendo video...")

    # Crear clip de video
    video_clip = ImageSequenceClip(frame_files, fps=fps)

    # Agregar audio
    audio_path = output_dir / "audio_converted.wav"
    if not audio_path.exists():
        audio_path = output_dir / "audio_original.wav"
    if not audio_path.exists():
        audio_path = output_dir / "audio_original.mpeg"

    if audio_path.exists():
        audio_clip = AudioFileClip(str(audio_path))
        video_clip = video_clip.with_audio(audio_clip)
        logger.info(f"🔊 Audio agregado: {audio_path.name}")

    # Guardar video
    output_path = output_dir / "scene_00s.mp4"
    video_clip.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        fps=fps,
        logger=None
    )

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ VIDEO GENERADO CON FAMILIA")
    logger.info("=" * 70)
    logger.info(f"📁 {output_path}")

    return str(output_path)


def main():
    """Generar video con familia para el directorio más reciente"""
    base_dir = Path(__file__).parent.parent.parent
    output_base = base_dir / "output"

    # Buscar directorio más reciente
    video_dirs = sorted([d for d in output_base.glob("*-*") if d.is_dir()], reverse=True)

    if not video_dirs:
        logger.error(f"❌ No se encontraron directorios en {output_base}")
        return False

    output_dir = video_dirs[0]
    logger.info(f"📁 Procesando: {output_dir.name}")

    # Cargar lip sync data
    lip_sync_path = output_dir / "lip_sync_data.json"
    if not lip_sync_path.exists():
        logger.error(f"❌ No se encontró lip_sync_data.json en {output_dir}")
        return False

    with open(lip_sync_path, 'r', encoding='utf-8') as f:
        lip_sync_data = json.load(f)

    logger.info(f"✅ Lip sync cargado: {lip_sync_data['duration']:.2f}s, {len(lip_sync_data['frame_states'])} frames")

    # Cargar animation plan
    animation_plan_path = output_dir / "animation_plan.json"
    if not animation_plan_path.exists():
        logger.error(f"❌ No se encontró animation_plan.json en {output_dir}")
        return False

    with open(animation_plan_path, 'r', encoding='utf-8') as f:
        animation_plan = json.load(f)

    logger.info(f"✅ Animation plan cargado: {len(animation_plan.get('characters', []))} personajes")

    # Buscar background
    background_path = output_dir / "fondo.png"
    if not background_path.exists():
        background_path = None

    # Generar video
    result = generate_video_family(
        output_dir,
        lip_sync_data,
        animation_plan,
        background_path=background_path,
        fps=30
    )

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
