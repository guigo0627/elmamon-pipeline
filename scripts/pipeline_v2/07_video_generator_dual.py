#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 7 DUAL: Video Generator con 2 Fondos
Genera frames animados alternando entre 2 backgrounds según quién habla
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

logger = setup_logger('video_gen_dual')

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


def create_gradient_background(size, color1=(100, 150, 255), color2=(150, 100, 200)):
    """Crea un fondo con gradiente simple"""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    for y in range(size[1]):
        # Interpolate between colors
        ratio = y / size[1]
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2]) * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))

    return img


def detect_speaker_from_lip_sync(frame_num, lip_sync_data, alternation_pattern=None):
    """
    Detecta quién está hablando en este frame

    Args:
        frame_num: Número de frame
        lip_sync_data: Datos de lip sync
        alternation_pattern: Patrón de alternancia (lista de tuplas (start_frame, speaker))

    Returns:
        str: 'char1' (papa - hombre) o 'char2' (mama - mujer)
    """
    if alternation_pattern:
        # Usar patrón predefinido
        for i, (start_frame, speaker) in enumerate(alternation_pattern):
            if i < len(alternation_pattern) - 1:
                end_frame = alternation_pattern[i + 1][0]
                if start_frame <= frame_num < end_frame:
                    return speaker
            else:
                if frame_num >= start_frame:
                    return speaker
        return 'char1'  # Default

    # Si no hay patrón: todo el hombre (para este caso específico)
    return 'char1'


def generate_frame_dual_background(
    frame_num,
    lip_sync_data,
    background1,  # Casa del hombre
    background2,  # Casa de la mujer
    alternation_pattern=None,
    output_size=(1080, 1920)
):
    """
    Genera un frame con background alternante según quién habla

    Args:
        frame_num: Número de frame
        lip_sync_data: Datos de lip sync
        background1: Background para char1 (papa)
        background2: Background para char2 (mama)
        alternation_pattern: Patrón de alternancia opcional
        output_size: Tamaño del output

    Returns:
        PIL Image del frame
    """
    # Detectar quién habla
    speaker = detect_speaker_from_lip_sync(frame_num, lip_sync_data, alternation_pattern)

    # Seleccionar background según quién habla
    background = background1.copy() if speaker == 'char1' else background2.copy()

    # Obtener mouth state del frame
    frame_state = lip_sync_data['frame_states'][frame_num]
    mouth_state = frame_state['mouth_state']

    # Parpadeo natural (cíclico)
    blink_cycle = 50  # Parpadea cada 50 frames (~1.6s)
    blink_duration = 3  # Duración del parpadeo: 3 frames

    # Para hombre: parpadea cuando tiene boca cerrada
    blink_hombre = (frame_num % blink_cycle) < blink_duration and mouth_state == 'closed'

    # Para mujer: parpadea siempre (cada 50 frames, independiente de mouth_state)
    blink_mujer = (frame_num % blink_cycle) < blink_duration

    # Floor position (90% de la altura)
    floor_y = int(output_size[1] * 0.90)
    char_height = int(output_size[1] * 0.75)

    if speaker == 'char1':
        # Mostrar PAPA (hombre) hablando por celular
        char_data = {'type': 'papa', 'position': 'center'}
        char_img = create_character_frame(
            char_data,
            expression='sumiso',
            gesture='phone_call',  # ✅ Celular en oreja
            mouth_state=mouth_state,  # Usa lip sync real
            width=600,
            height=1200,
            transparent_bg=True,
            blink=blink_hombre  # Parpadeo cuando boca cerrada
        )
    else:
        # Mostrar MAMA (mujer) SOLO ESCUCHANDO por celular
        char_data = {'type': 'mama', 'position': 'center'}
        char_img = create_character_frame(
            char_data,
            expression='disculpa',
            gesture='phone_call',  # ✅ Celular en oreja
            mouth_state='closed',  # SIEMPRE cerrada - solo escucha
            width=600,
            height=1200,
            transparent_bg=True,
            blink=blink_mujer  # Parpadeo cíclico cada ~1.6s
        )

    # Redimensionar personaje
    char_w = int(char_height * (char_img.width / char_img.height))
    char_img = char_img.resize((char_w, char_height), Image.Resampling.LANCZOS)

    # Posicionar en el centro
    x = (output_size[0] - char_w) // 2
    y = floor_y - char_height

    # Pegar personaje en el background
    background.paste(char_img, (x, y), char_img)

    return background


def create_alternation_pattern_minimal(total_frames, fps=30):
    """
    Crea patrón de alternancia con solo 2 apariciones de la mujer

    Args:
        total_frames: Total de frames del video
        fps: FPS del video

    Returns:
        list: Lista de (frame_start, speaker)
    """
    # La mujer aparece solo 2 veces en momentos clave
    # Resto del tiempo: hombre hablando

    duration_seconds = total_frames / fps

    # Primera aparición: 6 segundos (frame 180 @ 30fps)
    first_appearance_frame = int(6 * fps)  # 6 segundos exactos
    first_duration_frames = int(fps * 3)  # 3 segundos (para asegurar parpadeo)

    # Segunda aparición: ~75% del video (segundo ~20-22)
    second_appearance_frame = int(total_frames * 0.75)
    second_duration_frames = int(fps * 3)  # 3 segundos (para asegurar parpadeo)

    pattern = [
        (0, 'char1'),  # Hombre desde inicio
        (first_appearance_frame, 'char2'),  # Mujer aparece
        (first_appearance_frame + first_duration_frames, 'char1'),  # Vuelve hombre
        (second_appearance_frame, 'char2'),  # Mujer aparece otra vez
        (second_appearance_frame + second_duration_frames, 'char1'),  # Final: hombre
    ]

    logger.info("📊 Patrón de alternancia creado:")
    for frame, speaker in pattern:
        second = frame / fps
        char_name = "HOMBRE" if speaker == 'char1' else "MUJER"
        logger.info(f"   Frame {frame} ({second:.1f}s): {char_name}")

    return pattern


def generate_video_dual_backgrounds(
    output_dir,
    lip_sync_data,
    background1_path=None,
    background2_path=None,
    alternation_pattern=None,
    fps=30
):
    """
    Genera video completo con 2 backgrounds alternantes

    Args:
        output_dir: Directorio de salida
        lip_sync_data: Datos de lip sync
        background1_path: Path al background 1 (o None para gradiente)
        background2_path: Path al background 2 (o None para gradiente)
        alternation_pattern: Patrón de alternancia opcional (si None, usa minimal)
        fps: FPS del video

    Returns:
        str: Path al video generado
    """
    output_dir = Path(output_dir)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True, parents=True)

    output_size = (1080, 1920)

    logger.info("=" * 70)
    logger.info("🎬 GENERANDO VIDEO CON 2 FONDOS")
    logger.info("=" * 70)

    # Crear patrón minimal si no se proporcionó uno
    if alternation_pattern is None:
        total_frames = len(lip_sync_data['frame_states'])
        alternation_pattern = create_alternation_pattern_minimal(total_frames, fps)
        logger.info("✅ Usando patrón minimal: solo 2 apariciones de mujer")

    # Cargar o crear backgrounds
    if background1_path and Path(background1_path).exists():
        background1 = Image.open(background1_path).convert('RGBA')
        background1 = background1.resize(output_size, Image.Resampling.LANCZOS)
        logger.info(f"✅ Background 1 cargado: {Path(background1_path).name}")
    else:
        # Crear gradiente azul (casa del hombre)
        background1 = create_gradient_background(output_size, (80, 120, 200), (120, 80, 180))
        logger.info("🎨 Background 1: Gradiente azul (casa del hombre)")

    if background2_path and Path(background2_path).exists():
        background2 = Image.open(background2_path).convert('RGBA')
        background2 = background2.resize(output_size, Image.Resampling.LANCZOS)
        logger.info(f"✅ Background 2 cargado: {Path(background2_path).name}")
    else:
        # Crear gradiente rosa/morado (casa de la mujer)
        background2 = create_gradient_background(output_size, (180, 100, 150), (150, 120, 180))
        logger.info("🎨 Background 2: Gradiente rosa (casa de la mujer)")

    # Generar frames
    total_frames = len(lip_sync_data['frame_states'])
    logger.info(f"📊 Generando {total_frames} frames...")

    frame_files = []
    for frame_num in range(total_frames):
        if frame_num % 100 == 0:
            logger.info(f"  Frame {frame_num}/{total_frames} ({frame_num*100//total_frames}%)")

        frame = generate_frame_dual_background(
            frame_num,
            lip_sync_data,
            background1,
            background2,
            alternation_pattern,
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
    logger.info("✅ VIDEO GENERADO CON 2 FONDOS")
    logger.info("=" * 70)
    logger.info(f"📁 {output_path}")

    return str(output_path)


def main():
    """Generar video con 2 fondos para el directorio más reciente"""
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

    # Generar video
    result = generate_video_dual_backgrounds(
        output_dir,
        lip_sync_data,
        background1_path=None,  # Usar gradientes por ahora
        background2_path=None,
        alternation_pattern=None,  # Auto-detect alternation
        fps=30
    )

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
