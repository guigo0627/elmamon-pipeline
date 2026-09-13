#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Generación de Audio con ElevenLabs
Genera audio profesional a partir del guión
"""

import sys
import os
import json
import requests
import time
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, get_api_key

logger = setup_logger('audio_elevenlabs')

# Voces ElevenLabs (IDs de voces en español)
VOCES_ELEVENLABS = {
    'mama': 'EXAVITQu4vr4xnSDxMaL',  # Sarah - mujer latina
    'papa': '21m00Tcm4TlvDq8ikWAM',  # Rachel voice (ajustar según disponibles)
    'hijo1': 'pNInz6obpgDQGcFmaJgB',  # Adam - joven
    'hijo2': 'yoZ06aMxZJJ28mfd3POQ',  # Sam - joven
    'hijo_mayor': 'pNInz6obpgDQGcFmaJgB',
    'hijo_menor': 'yoZ06aMxZJJ28mfd3POQ',
    'amigo': '21m00Tcm4TlvDq8ikWAM',
    'default': 'EXAVITQu4vr4xnSDxMaL'
}


def generar_audio_elevenlabs(texto, voice_id, output_path, api_key):
    """
    Genera audio usando ElevenLabs API

    Args:
        texto: Texto a convertir en audio
        voice_id: ID de la voz en ElevenLabs
        output_path: Donde guardar el archivo MP3
        api_key: API key de ElevenLabs

    Returns:
        bool: True si exitoso
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    try:
        # Deshabilitar verificación SSL para entornos corporativos
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.post(url, json=data, headers=headers, verify=False)

        if response.status_code != 200:
            logger.error(f"❌ Error {response.status_code}: {response.text}")
            return False

        # Guardar audio
        with open(output_path, 'wb') as f:
            f.write(response.content)

        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def seleccionar_voz(personaje):
    """Selecciona voz apropiada para el personaje"""
    personaje_lower = personaje.lower()
    return VOCES_ELEVENLABS.get(personaje_lower, VOCES_ELEVENLABS['default'])


def generar_audios_dialogo(guion_path, output_dir, api_key):
    """
    Genera archivos de audio para cada línea de diálogo

    Args:
        guion_path: Ruta al guion.json
        output_dir: Carpeta donde guardar audios
        api_key: API key de ElevenLabs

    Returns:
        list: Lista de archivos de audio generados
    """
    logger.info(f"📖 Leyendo guión: {guion_path}")

    with open(guion_path, 'r', encoding='utf-8') as f:
        guion = json.load(f)

    dialogos = guion.get('dialogo', [])
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []

    for idx, linea in enumerate(dialogos):
        hablante = linea.get('hablante', 'default')
        texto = linea.get('linea', '')

        if not texto:
            logger.warning(f"⚠️ Línea {idx+1} vacía, saltando")
            continue

        # Seleccionar voz
        voice_id = seleccionar_voz(hablante)

        # Nombre del archivo
        filename = f"dialogo_{idx+1:02d}_{hablante}.mp3"
        output_path = output_dir / filename

        logger.info(f"🎤 Generando audio {idx+1}/{len(dialogos)}: {hablante}")
        logger.info(f"   Voice ID: {voice_id}")
        logger.info(f"   Texto: {texto[:60]}...")

        # Generar audio
        success = generar_audio_elevenlabs(texto, voice_id, str(output_path), api_key)

        if success:
            logger.info(f"✅ Audio guardado: {filename}")
            archivos_generados.append({
                'indice': idx,
                'hablante': hablante,
                'archivo': filename,
                'ruta': str(output_path),
                'texto': texto,
                'voice_id': voice_id
            })
        else:
            logger.error(f"❌ Falló generación de audio {idx+1}")

        # Rate limiting: esperar entre requests
        if idx < len(dialogos) - 1:
            time.sleep(1)

    return archivos_generados


def combinar_audios(archivos, output_path, silencio_entre_dialogos=0.5):
    """
    Combina múltiples archivos de audio en uno solo con pausas

    Args:
        archivos: Lista de rutas a archivos de audio
        output_path: Donde guardar el audio combinado
        silencio_entre_dialogos: Segundos de silencio entre diálogos

    Returns:
        bool: True si exitoso
    """
    logger.info(f"🔗 Combinando {len(archivos)} archivos de audio...")

    try:
        from pydub import AudioSegment

        # Crear silencio
        silencio = AudioSegment.silent(duration=int(silencio_entre_dialogos * 1000))

        # Combinar audios
        audio_final = AudioSegment.empty()

        for i, archivo in enumerate(archivos):
            ruta = archivo['ruta']
            logger.info(f"   Agregando: {Path(ruta).name}")

            audio = AudioSegment.from_mp3(ruta)
            audio_final += audio

            # Agregar silencio entre diálogos (excepto el último)
            if i < len(archivos) - 1:
                audio_final += silencio

        # Guardar
        audio_final.export(output_path, format="mp3")
        logger.info(f"✅ Audio combinado guardado: {output_path}")
        logger.info(f"   Duración total: {len(audio_final) / 1000:.2f} segundos")

        return True

    except ImportError:
        logger.error("❌ pydub no instalado. Instalar con: pip install pydub")
        logger.info("   También requiere ffmpeg")
        return False
    except Exception as e:
        logger.error(f"❌ Error combinando audios: {e}")
        return False


def main():
    """Pipeline de generación de audio"""
    logger.info("=" * 70)
    logger.info("🎤 GENERACIÓN DE AUDIO - ELEVENLABS")
    logger.info("=" * 70)

    # API key
    api_key = get_api_key('elevenlabs')
    if not api_key:
        logger.error("❌ No se encontró API key de ElevenLabs")
        logger.info("   Configurar en .env: ELEVENLABS_API_KEY=tu_api_key")
        return False

    # Configuración
    VIDEO_ID = "001"
    base_dir = Path(__file__).parent.parent
    output_base = base_dir / "output" / f"{VIDEO_ID}-20260904"
    audio_dir = output_base / "audio"
    guion_path = output_base / "guion.json"

    if not guion_path.exists():
        logger.error(f"❌ Guión no encontrado: {guion_path}")
        return False

    logger.info(f"📁 Video: {VIDEO_ID}")
    logger.info(f"📂 Carpeta audio: {audio_dir}")
    logger.info("")

    # Generar audios individuales
    archivos = generar_audios_dialogo(guion_path, audio_dir, api_key)

    if not archivos:
        logger.error("❌ No se generaron audios")
        return False

    logger.info("")
    logger.info(f"✅ {len(archivos)} archivos de audio generados")
    logger.info("")

    # Combinar en un solo archivo
    audio_final_path = audio_dir / "audio_completo.mp3"
    success = combinar_audios(archivos, audio_final_path)

    if not success:
        logger.warning("⚠️ No se pudo combinar audios (requiere pydub + ffmpeg)")
        logger.info("   Pero los archivos individuales están disponibles")

    # Guardar metadata
    metadata = {
        'video_id': VIDEO_ID,
        'archivos': archivos,
        'audio_completo': str(audio_final_path) if success else None,
        'total_dialogos': len(archivos)
    }

    metadata_path = audio_dir / "audio_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"📝 Metadata guardada: {metadata_path}")
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ GENERACIÓN DE AUDIO COMPLETADA")
    logger.info("=" * 70)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
