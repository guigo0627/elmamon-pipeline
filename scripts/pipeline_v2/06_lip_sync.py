#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 6: Lip Sync con Rhubarb
Genera mouth cues (formas de boca) sincronizados con audio
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

logger = setup_logger('lip_sync')


# Mapeo de mouth shapes de Rhubarb a nuestros estados
RHUBARB_TO_MOUTH_STATE = {
    'A': 'open',      # Open vowel (ah)
    'B': 'closed',    # Lips together (m, b, p)
    'C': 'semi',      # Rounded lips (oo, oh)
    'D': 'semi',      # Teeth (th, s, z)
    'E': 'semi',      # Narrow (ee, i)
    'F': 'closed',    # Lower lip teeth (f, v)
    'G': 'semi',      # Back of tongue (k, g)
    'H': 'semi',      # Tongue tip (l, n, t, d)
    'X': 'closed',    # Silence/rest
}


def run_rhubarb(audio_path, output_path=None):
    """
    Ejecuta Rhubarb para generar mouth cues

    Args:
        audio_path: Ruta al archivo de audio
        output_path: Donde guardar el JSON (opcional)

    Returns:
        dict: Mouth cues con timestamps
    """
    base_dir = Path(__file__).parent.parent.parent
    rhubarb_path = base_dir / "tools" / "rhubarb" / "Rhubarb-Lip-Sync-1.13.0-Windows" / "rhubarb.exe"

    if not rhubarb_path.exists():
        logger.error(f"❌ Rhubarb no encontrado: {rhubarb_path}")
        return None

    audio_path = Path(audio_path)
    if not audio_path.exists():
        logger.error(f"❌ Audio no encontrado: {audio_path}")
        return None

    # Rhubarb solo acepta WAV/OGG
    # Convertir si es necesario
    if audio_path.suffix.lower() not in ['.wav', '.ogg']:
        logger.info(f"⚠️  Rhubarb requiere WAV/OGG, convirtiendo...")
        wav_path = audio_path.with_suffix('.wav')

        # Convertir con ffmpeg (procesando TODO el audio)
        import subprocess
        try:
            # Comando ffmpeg correcto: opciones ANTES del archivo de salida
            subprocess.run([
                'ffmpeg',
                '-y',            # Overwrite (debe ir ANTES de -i)
                '-i', str(audio_path),
                '-ar', '22050',  # Sample rate 22.05kHz (evita truncamiento de audio)
                '-ac', '1',      # Mono
                str(wav_path)
            ], capture_output=True, check=True, timeout=60)

            audio_path = wav_path
            logger.info(f"   ✅ Convertido a: {wav_path.name}")
        except Exception as e:
            logger.error(f"❌ Error convirtiendo audio: {e}")
            return None

    logger.info(f"🎤 Ejecutando Rhubarb lip sync...")
    logger.info(f"   Audio: {audio_path.name}")

    # Ejecutar Rhubarb
    try:
        cmd = [
            str(rhubarb_path),
            str(audio_path),
            "-f", "json",  # Output formato JSON
            "--extendedShapes", "GHX"  # Shapes extendidas
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.error(f"❌ Error en Rhubarb: {result.stderr}")
            return None

        # Parse JSON output
        rhubarb_data = json.loads(result.stdout)

        logger.info(f"✅ Rhubarb completado")
        logger.info(f"   Duración: {rhubarb_data['metadata']['duration']:.2f}s")
        logger.info(f"   Mouth cues: {len(rhubarb_data['mouthCues'])}")

        # Guardar si se especifica
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rhubarb_data, f, indent=2)
            logger.info(f"💾 Guardado: {output_path}")

        return rhubarb_data

    except subprocess.TimeoutExpired:
        logger.error("❌ Rhubarb timeout (>60s)")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


def process_mouth_cues(rhubarb_data, fps=30, real_duration=None):
    """
    Procesa mouth cues de Rhubarb a formato por frame

    Args:
        rhubarb_data: Output de Rhubarb
        fps: Frames por segundo del video
        real_duration: Duración real del audio (si es mayor que Rhubarb, extiende con boca cerrada)

    Returns:
        list: Mouth state por frame [0] = frame 0, etc.
    """
    rhubarb_duration = rhubarb_data['metadata']['duration']

    # Usar la duración mayor para generar frames completos
    if real_duration and real_duration > rhubarb_duration:
        duration = real_duration
        logger.info(f"📏 Extendiendo de {rhubarb_duration:.2f}s a {real_duration:.2f}s con boca cerrada")
    else:
        duration = rhubarb_duration

    total_frames = int(duration * fps)

    mouth_cues = rhubarb_data['mouthCues']

    # Array de mouth states por frame
    frame_states = []

    cue_idx = 0
    for frame in range(total_frames):
        time = frame / fps

        # Encontrar el cue activo en este tiempo
        while cue_idx < len(mouth_cues) - 1 and mouth_cues[cue_idx + 1]['start'] <= time:
            cue_idx += 1

        # Obtener shape de Rhubarb
        rhubarb_shape = mouth_cues[cue_idx]['value']

        # Convertir a nuestro estado
        mouth_state = RHUBARB_TO_MOUTH_STATE.get(rhubarb_shape, 'closed')

        frame_states.append({
            'frame': frame,
            'time': time,
            'mouth_state': mouth_state,
            'rhubarb_shape': rhubarb_shape
        })

    logger.info(f"📊 Procesados {total_frames} frames a {fps} FPS")

    return frame_states


def generate_lip_sync_data(audio_path, output_dir, fps=30):
    """
    Genera datos completos de lip sync para un audio

    Args:
        audio_path: Ruta al audio
        output_dir: Directorio de salida
        fps: FPS del video

    Returns:
        dict: Lip sync data completo
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    logger.info("=" * 70)
    logger.info("🎤 GENERACIÓN DE LIP SYNC")
    logger.info("=" * 70)

    # 0. Obtener duración REAL del audio original
    try:
        from moviepy import AudioFileClip
        audio_clip = AudioFileClip(str(audio_path))
        real_duration = audio_clip.duration
        audio_clip.close()
        logger.info(f"⏱️  Duración audio original: {real_duration:.2f}s")
    except Exception as e:
        logger.warning(f"⚠️  No se pudo leer duración del audio: {e}")
        real_duration = None

    # 1. Ejecutar Rhubarb
    rhubarb_path = output_dir / "rhubarb_raw.json"
    rhubarb_data = run_rhubarb(audio_path, rhubarb_path)

    if not rhubarb_data:
        return None

    # 2. Procesar a frames (usando duración real si está disponible)
    if real_duration:
        frame_states = process_mouth_cues(rhubarb_data, fps, real_duration=real_duration)
        final_duration = real_duration
    else:
        frame_states = process_mouth_cues(rhubarb_data, fps)
        final_duration = rhubarb_data['metadata']['duration']

    # 3. Crear estructura final
    lip_sync_data = {
        'audio_file': str(Path(audio_path).name),
        'duration': final_duration,
        'fps': fps,
        'total_frames': len(frame_states),
        'frame_states': frame_states,
        'rhubarb_metadata': rhubarb_data['metadata']
    }

    # 4. Guardar
    output_path = output_dir / "lip_sync_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lip_sync_data, f, indent=2)

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ LIP SYNC DATA GENERADO")
    logger.info("=" * 70)
    logger.info(f"📁 {output_path}")
    logger.info(f"⏱️  Duración: {lip_sync_data['duration']:.2f}s")
    logger.info(f"🎬 Frames: {lip_sync_data['total_frames']}")

    return lip_sync_data


def main():
    """Test del módulo"""
    base_dir = Path(__file__).parent.parent.parent

    # Usar directorio de argumentos de línea de comandos si se proporciona
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        output_dir = base_dir / "output" / "001-20260910"

    audio_path = output_dir / "audio_original.mpeg"

    if not audio_path.exists():
        logger.error(f"❌ Audio no encontrado: {audio_path}")
        return False

    lip_sync_data = generate_lip_sync_data(audio_path, output_dir, fps=30)

    if lip_sync_data:
        logger.info("\n🎉 Lip sync data listo para usar en animación")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
