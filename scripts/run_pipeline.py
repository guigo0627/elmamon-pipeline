#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE MAESTRO
Ejecuta todos los módulos end-to-end para generar videos animados
"""

import sys
import os
from pathlib import Path
import json
import time

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent))
from utils import setup_logger

logger = setup_logger('pipeline')


def run_pipeline(audio_path, output_name=None):
    """
    Ejecuta el pipeline completo

    Args:
        audio_path: Ruta al archivo de audio MP3/MPEG
        output_name: Nombre del directorio de salida (opcional)

    Returns:
        dict: Resultados del pipeline
    """
    logger.info("=" * 80)
    logger.info("🎬 PIPELINE DE GENERACIÓN DE VIDEOS ANIMADOS")
    logger.info("=" * 80)

    start_time = time.time()

    # Preparar directorios
    base_dir = Path(__file__).parent.parent
    audio_path = Path(audio_path)

    if not audio_path.exists():
        logger.error(f"❌ Audio no encontrado: {audio_path}")
        return None

    # Crear directorio de salida
    if output_name is None:
        from datetime import datetime
        output_name = f"{len(list((base_dir / 'output').glob('*')))+1:03d}-{datetime.now().strftime('%Y%m%d')}"

    output_dir = base_dir / "output" / output_name
    output_dir.mkdir(exist_ok=True, parents=True)

    # Copiar audio al output
    import shutil
    audio_copy = output_dir / "audio_original.mpeg"
    shutil.copy(audio_path, audio_copy)

    logger.info(f"📁 Output: {output_dir.name}")
    logger.info("")

    results = {
        'audio_path': str(audio_copy),
        'output_dir': str(output_dir)
    }

    try:
        # MÓDULO 01: Transcripción
        logger.info("=" * 80)
        logger.info("📝 PASO 1: TRANSCRIPCIÓN")
        logger.info("=" * 80)

        from pipeline_v2.transcribe import transcribe_audio
        transcription = transcribe_audio(audio_copy, output_dir)

        if not transcription:
            logger.error("❌ Error en transcripción")
            return None

        results['transcription'] = str(output_dir / "transcription.json")
        logger.info(f"✅ Transcripción completada")
        logger.info("")

        # MÓDULO 02: Análisis (AGENTE 1)
        logger.info("=" * 80)
        logger.info("🤖 PASO 2: ANÁLISIS CONTEXTUAL (AGENTE 1)")
        logger.info("=" * 80)

        # NOTE: AGENTE 1 ya debe haber generado animation_plan.json
        # Por ahora, verificamos que existe
        animation_plan_path = output_dir / "animation_plan.json"
        if not animation_plan_path.exists():
            logger.error("❌ animation_plan.json no encontrado")
            logger.info("   Genera manualmente con AGENTE 1")
            return None

        with open(animation_plan_path, 'r', encoding='utf-8') as f:
            animation_plan = json.load(f)

        results['animation_plan'] = str(animation_plan_path)
        logger.info(f"✅ Plan de animación cargado")
        logger.info(f"   Personajes: {animation_plan['analysis']['characters_in_scene']}")
        logger.info(f"   Escenas: {len(animation_plan['scenes'])}")
        logger.info(f"   Escenario: {animation_plan['analysis']['background_analysis']['recommended_setting']}")
        logger.info("")

        # MÓDULO 04: Background
        logger.info("=" * 80)
        logger.info("🖼️  PASO 3: BACKGROUND")
        logger.info("=" * 80)

        from pipeline_v2.background_manager import get_background_for_video
        background_path = get_background_for_video(animation_plan_path, output_dir / "backgrounds")

        if not background_path:
            logger.error("❌ Error obteniendo background")
            return None

        results['background'] = str(background_path)
        logger.info("")

        # MÓDULO 06: Lip Sync
        logger.info("=" * 80)
        logger.info("🎤 PASO 4: LIP SYNC")
        logger.info("=" * 80)

        from pipeline_v2.lip_sync import generate_lip_sync_data
        lip_sync_data = generate_lip_sync_data(audio_copy, output_dir, fps=30)

        if not lip_sync_data:
            logger.error("❌ Error en lip sync")
            return None

        results['lip_sync'] = str(output_dir / "lip_sync_data.json")
        logger.info("")

        # MÓDULO 07: Generación de Video
        logger.info("=" * 80)
        logger.info("🎬 PASO 5: GENERACIÓN DE VIDEO")
        logger.info("=" * 80)

        from pipeline_v2.video_generator import generate_video_segment

        # Por ahora: generar solo primeros 3 segundos
        start_frame = 0
        end_frame = min(90, lip_sync_data['total_frames'])  # 3s o menos

        video_path = generate_video_segment(
            start_frame, end_frame,
            output_dir, audio_copy,
            lip_sync_data, animation_plan,
            background_path, fps=30
        )

        results['video'] = video_path
        logger.info("")

        # RESUMEN FINAL
        elapsed = time.time() - start_time
        logger.info("=" * 80)
        logger.info("🎉 PIPELINE COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"⏱️  Tiempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        logger.info(f"📁 Output: {output_dir}")
        logger.info(f"🎬 Video: {video_path}")
        logger.info("")

        return results

    except Exception as e:
        logger.error(f"❌ Error en pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Ejecutar pipeline con audio de prueba"""
    base_dir = Path(__file__).parent.parent
    audio_path = base_dir / "assets" / "input_audios" / "Audio_prueba.mpeg"

    if not audio_path.exists():
        # Buscar en output si no está en assets
        audio_path = base_dir / "output" / "001-20260910" / "audio_original.mpeg"

    if not audio_path.exists():
        logger.error(f"❌ Audio no encontrado: {audio_path}")
        return False

    results = run_pipeline(audio_path, output_name="001-20260910")

    if results:
        logger.info("✅ Pipeline ejecutado exitosamente")
        return True
    else:
        logger.error("❌ Pipeline falló")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
