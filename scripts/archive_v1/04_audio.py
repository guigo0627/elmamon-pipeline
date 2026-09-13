#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Generación de Audio
Genera audio a partir del guión usando Edge-TTS (Microsoft, gratis)
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger

logger = setup_logger('audio')

# Intentar importar edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("⚠️ edge-tts no instalado. Instalar con: pip install edge-tts")


# Voces en español (Edge-TTS)
VOCES_EDGE = {
    'mama': 'es-MX-DaliaNeural',      # Mujer mexicana
    'papa': 'es-MX-JorgeNeural',      # Hombre mexicano
    'hijo1': 'es-MX-BeatrizNeural',   # Mujer joven (para hijo adolescente)
    'hijo2': 'es-MX-LibertoNeural',   # Hombre joven
    'hijo_mayor': 'es-MX-BeatrizNeural',
    'hijo_menor': 'es-MX-LibertoNeural',
    'amigo': 'es-MX-JorgeNeural',
    'default': 'es-MX-DaliaNeural'
}


async def generar_audio_edge(texto, voz, output_path):
    """
    Genera audio usando Edge-TTS

    Args:
        texto: Texto a convertir en audio
        voz: Nombre de la voz (ej: 'es-MX-DaliaNeural')
        output_path: Donde guardar el archivo MP3

    Returns:
        bool: True si exitoso
    """
    try:
        communicate = edge_tts.Communicate(texto, voz)
        await communicate.save(output_path)
        return True
    except Exception as e:
        logger.error(f"❌ Error generando audio: {e}")
        return False


def seleccionar_voz(personaje):
    """Selecciona voz apropiada para el personaje"""
    personaje_lower = personaje.lower()
    return VOCES_EDGE.get(personaje_lower, VOCES_EDGE['default'])


async def generar_audios_dialogo(guion_path, output_dir):
    """
    Genera archivos de audio para cada línea de diálogo

    Args:
        guion_path: Ruta al guion.json
        output_dir: Carpeta donde guardar audios

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
        voz = seleccionar_voz(hablante)

        # Nombre del archivo
        filename = f"dialogo_{idx+1:02d}_{hablante}.mp3"
        output_path = output_dir / filename

        logger.info(f"🎤 Generando audio {idx+1}/{len(dialogos)}: {hablante}")
        logger.info(f"   Voz: {voz}")
        logger.info(f"   Texto: {texto[:60]}...")

        # Generar audio
        success = await generar_audio_edge(texto, voz, str(output_path))

        if success:
            logger.info(f"✅ Audio guardado: {filename}")
            archivos_generados.append({
                'indice': idx,
                'hablante': hablante,
                'archivo': filename,
                'ruta': str(output_path),
                'texto': texto,
                'voz': voz
            })
        else:
            logger.error(f"❌ Falló generación de audio {idx+1}")

    return archivos_generados


async def combinar_audios(archivos, output_path, silencio_entre_dialogos=0.5):
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
        from pydub.silence import generate_silence

        # Crear silencio
        silencio = generate_silence(duration=int(silencio_entre_dialogos * 1000))

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


async def main():
    """Pipeline de generación de audio"""
    logger.info("=" * 70)
    logger.info("🎤 GENERACIÓN DE AUDIO")
    logger.info("=" * 70)

    if not EDGE_TTS_AVAILABLE:
        logger.error("❌ edge-tts no está instalado")
        logger.info("   Instalar con: pip install edge-tts")
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
    archivos = await generar_audios_dialogo(guion_path, audio_dir)

    if not archivos:
        logger.error("❌ No se generaron audios")
        return False

    logger.info("")
    logger.info(f"✅ {len(archivos)} archivos de audio generados")
    logger.info("")

    # Combinar en un solo archivo
    audio_final_path = audio_dir / "audio_completo.mp3"
    success = await combinar_audios(archivos, audio_final_path)

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
    if sys.platform == 'win32':
        # Windows requiere configuración especial para asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
