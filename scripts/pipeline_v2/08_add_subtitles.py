#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 8: Subtítulos Karaoke (formato ASS)
Agrega subtítulos con efecto karaoke usando formato ASS + ffmpeg burn-in
"""

import sys
import os
from pathlib import Path
import json
import subprocess

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('subtitles')


# Configuración para formato 9:16 (Shorts)
SUBTITLE_CONFIG = {
    'font_size': 90,
    'outline': 6,
    'margin_v': 380,
    'alignment': 2,  # Centro inferior
    'primary_color': '&H0000FFFF',  # Amarillo neón (karaoke final)
    'secondary_color': '&H00FFFFFF',  # Blanco (inicial)
    'outline_color': '&H00000000',  # Negro
    'back_color': '&H80000000',  # Semi-transparente
}


def format_timestamp_ass(seconds):
    """
    Formatea timestamp para formato ASS

    Args:
        seconds: Tiempo en segundos

    Returns:
        str: Timestamp formato ASS (0:00:00.00)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def create_karaoke_text_from_words(words, segment_start, segment_end):
    """
    Crea texto con efecto karaoke usando word timestamps

    Args:
        words: Lista de palabras con timestamps de AssemblyAI
        segment_start: Inicio del segmento (ms)
        segment_end: Fin del segmento (ms)

    Returns:
        str: Texto con tags de karaoke (\k)
    """
    karaoke_text = ""
    prev_end = segment_start

    for word_info in words:
        word_text = word_info.get('text', '').strip()
        word_start = word_info.get('start', prev_end)  # En milisegundos
        word_end = word_info.get('end', word_start + 500)

        # Convertir a segundos
        word_start_s = word_start / 1000
        word_end_s = word_end / 1000
        prev_end_s = prev_end / 1000

        # Duración en centésimas de segundo (para tag \k)
        duration_cs = int((word_end_s - word_start_s) * 100)

        # Si hay gap antes de esta palabra, agregar pausa
        gap = word_start_s - prev_end_s
        if gap > 0.05:  # Gap mayor a 50ms
            gap_cs = int(gap * 100)
            karaoke_text += f"{{\\k{gap_cs}}} "

        # Agregar palabra con su duración
        karaoke_text += f"{{\\k{duration_cs}}}{word_text} "
        prev_end = word_end

    return karaoke_text.strip()


def create_ass_file(transcription_path, output_ass_path):
    """
    Crea archivo ASS con efecto karaoke desde transcription.json

    Args:
        transcription_path: Path a transcription.json (de AssemblyAI)
        output_ass_path: Path del archivo ASS de salida

    Returns:
        bool: True si éxito
    """
    logger.info("📝 Creando archivo ASS con efecto karaoke...")

    # Leer transcripción
    with open(transcription_path, 'r', encoding='utf-8') as f:
        transcription = json.load(f)

    config = SUBTITLE_CONFIG

    # Header ASS para 9:16
    ass_content = f"""[Script Info]
Title: Subtítulos Karaoke
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat,{config['font_size']},{config['primary_color']},{config['secondary_color']},{config['outline_color']},{config['back_color']},-1,0,0,0,100,100,0,0,1,{config['outline']},2,{config['alignment']},40,40,{config['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Agrupar palabras por segmentos (cada 3-5 palabras o por pausas)
    words = transcription.get('words', [])

    if not words:
        logger.warning("⚠️  No hay word-level timestamps en transcripción")
        # Fallback: usar texto completo
        text_full = transcription.get('text_full', '')
        start = format_timestamp_ass(0)
        end = format_timestamp_ass(transcription.get('audio_duration', 10))
        ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text_full}\n"
    else:
        # Agrupar palabras por segmentos (cada ~2-3 segundos)
        segments = []
        current_segment = []
        segment_start = None

        for i, word_info in enumerate(words):
            word_start = word_info['start'] / 1000  # ms a segundos

            if segment_start is None:
                segment_start = word_start

            current_segment.append(word_info)

            # Crear segmento cada ~3 segundos o al final
            duration = word_start - segment_start
            is_last = (i == len(words) - 1)

            if duration >= 3.0 or is_last:
                segments.append({
                    'start': segment_start,
                    'end': current_segment[-1]['end'] / 1000,
                    'words': current_segment
                })
                current_segment = []
                segment_start = None

        # Generar diálogos ASS
        for segment in segments:
            start = format_timestamp_ass(segment['start'])
            end = format_timestamp_ass(segment['end'])

            # Crear texto karaoke
            karaoke_text = create_karaoke_text_from_words(
                segment['words'],
                segment['words'][0]['start'],
                segment['words'][-1]['end']
            )

            # Escapar caracteres especiales
            karaoke_text = karaoke_text.replace('\n', '\\N')

            ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{karaoke_text}\n"

        logger.info(f"   {len(segments)} segmentos de subtítulos creados")

    # Guardar archivo
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)

    logger.info(f"✅ Archivo ASS creado: {output_ass_path}")
    return True


def burn_subtitles(video_path, ass_path, output_path):
    """
    Quema subtítulos ASS en el video usando ffmpeg

    Args:
        video_path: Path al video sin subtítulos
        ass_path: Path al archivo ASS
        output_path: Path del video con subtítulos

    Returns:
        bool: True si éxito
    """
    logger.info("🔥 Quemando subtítulos en video...")

    try:
        # Escapar rutas para ffmpeg (Windows paths con backslashes)
        ass_path_escaped = str(ass_path).replace('\\', '\\\\\\\\').replace(':', '\\\\:')

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vf', f"ass='{ass_path_escaped}'",
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600
        )

        if result.returncode != 0:
            logger.error(f"❌ Error en ffmpeg: {result.stderr.decode('utf-8', errors='ignore')}")
            return False

        logger.info(f"✅ Video con subtítulos: {output_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Error quemando subtítulos: {e}")
        return False


def add_subtitles_to_video(video_path, transcription_path, output_path=None):
    """
    Agrega subtítulos karaoke al video

    Args:
        video_path: Path al video sin subtítulos
        transcription_path: Path a transcription.json
        output_path: Path del video con subtítulos (opcional)

    Returns:
        str: Path al video con subtítulos o None si falla
    """
    logger.info("=" * 70)
    logger.info("📝 AGREGANDO SUBTÍTULOS KARAOKE")
    logger.info("=" * 70)

    video_path = Path(video_path)
    transcription_path = Path(transcription_path)

    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_subtitled{video_path.suffix}"
    else:
        output_path = Path(output_path)

    # 1. Crear archivo ASS
    ass_path = video_path.parent / f"{video_path.stem}.ass"

    if not create_ass_file(transcription_path, ass_path):
        return None

    # 2. Quemar subtítulos con ffmpeg
    if not burn_subtitles(video_path, ass_path, output_path):
        return None

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ SUBTÍTULOS KARAOKE AGREGADOS")
    logger.info("=" * 70)
    logger.info(f"📁 {output_path}")

    return str(output_path)


def main():
    """Test del módulo"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "output" / "001-20260910"

    video_path = output_dir / "scene_00s.mp4"
    transcription_path = output_dir / "transcription.json"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        # Buscar video completo
        video_path = output_dir / "scene_00s.mp4"

    if not transcription_path.exists():
        logger.error(f"❌ Transcripción no encontrada: {transcription_path}")
        return False

    result = add_subtitles_to_video(video_path, transcription_path)

    if result:
        logger.info(f"\n🎉 Video con subtítulos listo")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
