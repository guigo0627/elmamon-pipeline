#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 1: Transcripción con AssemblyAI
Input:  Audio MP3/MPEG
Output: transcription.json (con speaker diarization y timestamps)
"""

import sys
import os
import json
from pathlib import Path
import time

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('transcribe')

try:
    import assemblyai as aai
    # Fix SSL para PC corporativo - Monkey patch httpx
    import ssl
    import httpx
    import urllib3

    # Deshabilitar warnings SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Monkey patch httpx.Client para deshabilitar verify por defecto
    _original_httpx_client_init = httpx.Client.__init__
    def patched_init(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_httpx_client_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_init

    ssl._create_default_https_context = ssl._create_unverified_context
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False
    logger.error("❌ AssemblyAI no instalado: pip install assemblyai")

# Configuración
from pipeline_v2.config import ASSEMBLYAI_API_KEY, TRANSCRIPTION_CONFIG


def transcribe_audio(audio_path, output_dir):
    """
    Transcribe audio con AssemblyAI

    Args:
        audio_path: Ruta al audio MP3/MPEG
        output_dir: Directorio de salida

    Returns:
        dict: Transcripción con timestamps y speakers
    """
    if not ASSEMBLYAI_AVAILABLE:
        logger.error("❌ AssemblyAI no disponible")
        return None

    if not ASSEMBLYAI_API_KEY:
        logger.error("❌ ASSEMBLYAI_API_KEY no configurada en .env")
        logger.info("   Obtén una key gratuita en: https://www.assemblyai.com/")
        return None

    audio_path = Path(audio_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "transcription.json"

    logger.info("=" * 70)
    logger.info("🎙️  TRANSCRIPCIÓN CON ASSEMBLYAI")
    logger.info("=" * 70)
    logger.info(f"📁 Audio: {audio_path.name}")
    logger.info(f"📂 Output: {output_file}")
    logger.info("")

    try:
        # Configurar cliente
        aai.settings.api_key = ASSEMBLYAI_API_KEY

        # Configuración de transcripción
        config = aai.TranscriptionConfig(
            language_code=TRANSCRIPTION_CONFIG['language'],
            speaker_labels=TRANSCRIPTION_CONFIG['speaker_labels'],
            sentiment_analysis=TRANSCRIPTION_CONFIG['sentiment_analysis'],
            punctuate=True,
            format_text=True,
        )

        # Subir y transcribir
        logger.info("📤 Subiendo audio a AssemblyAI...")
        transcriber = aai.Transcriber(config=config)

        logger.info("🔄 Transcribiendo (esto puede tomar 30-60 segundos)...")
        transcript = transcriber.transcribe(str(audio_path))

        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"❌ Error: {transcript.error}")
            return None

        logger.info("✅ Transcripción completada!")
        logger.info("")

        # Procesar resultados
        logger.info("📊 Procesando resultados...")

        # Obtener speakers únicos
        speakers_data = {}
        if transcript.utterances:
            for utterance in transcript.utterances:
                speaker = utterance.speaker
                if speaker not in speakers_data:
                    speakers_data[speaker] = {
                        'speaker_id': speaker,
                        'segments': []
                    }

                # Agregar segmento
                segment = {
                    'start': utterance.start / 1000.0,  # ms a segundos
                    'end': utterance.end / 1000.0,
                    'text': utterance.text,
                    'confidence': utterance.confidence,
                }

                # Agregar sentiment si disponible
                if TRANSCRIPTION_CONFIG['sentiment_analysis'] and hasattr(utterance, 'sentiment'):
                    segment['sentiment'] = utterance.sentiment

                speakers_data[speaker]['segments'].append(segment)

        # Construir output
        result = {
            'audio_file': audio_path.name,
            'audio_duration': transcript.audio_duration / 1000.0 if transcript.audio_duration else 0,
            'language': TRANSCRIPTION_CONFIG['language'],
            'transcription_id': transcript.id,
            'text_full': transcript.text,
            'speakers': list(speakers_data.values()),
            'word_count': len(transcript.text.split()) if transcript.text else 0,
            'metadata': {
                'transcribed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'confidence': transcript.confidence if hasattr(transcript, 'confidence') else None,
            }
        }

        # Guardar
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ TRANSCRIPCIÓN GUARDADA")
        logger.info("=" * 70)
        logger.info(f"📄 {output_file}")
        logger.info(f"⏱️  Duración: {result['audio_duration']:.2f}s")
        logger.info(f"👥 Speakers detectados: {len(speakers_data)}")
        logger.info(f"📝 Palabras: {result['word_count']}")
        logger.info("=" * 70)
        logger.info("")

        # Mostrar preview
        logger.info("📋 PREVIEW:")
        for i, speaker_data in enumerate(result['speakers']):
            logger.info(f"\n🗣️  Speaker {speaker_data['speaker_id']}:")
            for seg in speaker_data['segments'][:2]:  # Primeros 2 segmentos
                logger.info(f"   [{seg['start']:.2f}s-{seg['end']:.2f}s] {seg['text'][:80]}...")
            if len(speaker_data['segments']) > 2:
                logger.info(f"   ... ({len(speaker_data['segments']) - 2} segmentos más)")

        logger.info("")

        return result

    except Exception as e:
        logger.error(f"❌ Error en transcripción: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Test del módulo"""
    logger.info("🎙️  Test módulo de transcripción")
    logger.info("")

    # Buscar audio de prueba
    base_dir = Path(__file__).parent.parent.parent
    audio_path = base_dir / "assets" / "input_audios" / "Audio_prueba.mpeg"

    if not audio_path.exists():
        logger.error(f"❌ Audio no encontrado: {audio_path}")
        return False

    # Output
    output_dir = base_dir / "output" / "test_transcription"

    # Transcribir
    result = transcribe_audio(audio_path, output_dir)

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
