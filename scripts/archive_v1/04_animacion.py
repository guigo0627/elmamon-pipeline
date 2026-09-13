#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Animación - Meta Animated Drawings + Rhubarb Lip Sync
Genera animación de personajes con lip sync
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger
from listar_personajes import validar_personaje_expresion, escanear_personajes

logger = setup_logger('animacion')


def seleccionar_expresion_por_dialogo(dialogo, personaje):
    """
    Analiza el diálogo y selecciona la expresión apropiada

    Args:
        dialogo: Texto del diálogo
        personaje: Nombre del personaje

    Returns:
        str: Expresión a usar (ej: 'enojada', 'sorprendido')
    """
    dialogo_lower = dialogo.lower()

    # Mapeo de keywords a expresiones
    keywords_expresiones = {
        'enojada': ['noooo', 'güey', 'no mijo', 'errrdaaaa'],
        'sorprendido': ['qué', 'cómo', 'universo', 'cósmica'],
        'llorando': ['llor', 'triste', 'cry'],
        'regañado': ['regañ', 'malo', 'castigo'],
    }

    # Buscar keywords en el diálogo
    for expresion, keywords in keywords_expresiones.items():
        for keyword in keywords:
            if keyword in dialogo_lower:
                # Verificar si la expresión existe para este personaje
                valido, _ = validar_personaje_expresion(personaje, expresion)
                if valido:
                    return expresion

    # Default: usar 'base'
    return 'base'


def analizar_guion_expresiones(guion_path):
    """
    Analiza guión y determina qué expresiones usar en cada momento

    Args:
        guion_path: Ruta al archivo guion.json

    Returns:
        list: Lista de escenas con personaje y expresión
    """
    logger.info(f"📖 Analizando guión: {guion_path}")

    with open(guion_path, 'r', encoding='utf-8') as f:
        guion = json.load(f)

    escenas = []
    personajes_disponibles = escanear_personajes()

    for idx, linea in enumerate(guion.get('dialogo', [])):
        hablante = linea.get('hablante')
        texto = linea.get('linea', '')

        # Mapear nombre de hablante a personaje disponible
        # Ej: "mamá" → "mama", "hijo_mayor" → "hijo1"
        personaje_real = mapear_hablante_a_personaje(hablante, personajes_disponibles)

        if not personaje_real:
            logger.warning(f"⚠️ Personaje '{hablante}' no encontrado, usando 'base'")
            continue

        # Seleccionar expresión según diálogo
        expresion = seleccionar_expresion_por_dialogo(texto, personaje_real)

        logger.info(f"  Escena {idx+1}: {personaje_real} ({expresion}) → \"{texto[:50]}...\"")

        escenas.append({
            'indice': idx,
            'personaje': personaje_real,
            'expresion': expresion,
            'dialogo': texto,
            'hablante_original': hablante,
            'timestamp': idx * 3  # Estimado: 3 segundos por escena
        })

    return escenas


def mapear_hablante_a_personaje(hablante, personajes_disponibles):
    """
    Mapea nombre del guión a personaje disponible

    Ejemplos:
        "mamá" → "mama"
        "hijo_mayor" → "hijo1"
        "papá" → "papa"
    """
    # Normalizar nombre
    nombre_norm = hablante.lower().replace('á', 'a').replace('é', 'e')

    # Mapeo directo
    mapeo = {
        'mama': 'mama',
        'papa': 'papa',
        'hijo_mayor': 'hijo1',
        'hijo_menor': 'hijo2',
        'amigo': 'amigo',
    }

    if nombre_norm in mapeo:
        personaje = mapeo[nombre_norm]
        if personaje in personajes_disponibles:
            return personaje

    # Buscar coincidencia parcial
    for personaje in personajes_disponibles:
        if personaje in nombre_norm or nombre_norm in personaje:
            return personaje

    return None


def animar_personaje_meta(imagen_path, output_path, movimiento="idle"):
    """
    Anima personaje usando Meta Animated Drawings

    Args:
        imagen_path: Ruta a imagen del personaje
        output_path: Donde guardar animación
        movimiento: Tipo de movimiento ("idle", "wave", "walk")

    Returns:
        bool: True si exitoso
    """
    logger.info(f"🎬 Animando personaje: {Path(imagen_path).name}")

    # TODO: Implementar llamada a Meta Animated Drawings
    # Por ahora, placeholder
    logger.info(f"   Entrada: {imagen_path}")
    logger.info(f"   Salida: {output_path}")
    logger.info(f"   Movimiento: {movimiento}")

    # Comando de ejemplo (ajustar según instalación real):
    # python -m animated_drawings.animate --image {imagen_path} --output {output_path}

    return True


def generar_lipsync_rhubarb(audio_path, output_path):
    """
    Genera datos de lip sync usando Rhubarb

    Args:
        audio_path: Ruta al archivo de audio
        output_path: Donde guardar JSON de visemas

    Returns:
        dict: Datos de visemas (mouth shapes)
    """
    logger.info(f"👄 Generando lip sync para: {Path(audio_path).name}")

    # Ruta a ejecutable de Rhubarb
    rhubarb_exe = Path(__file__).parent.parent / "tools" / "rhubarb" / "Rhubarb-Lip-Sync-1.13.0-Windows" / "rhubarb.exe"

    if not rhubarb_exe.exists():
        logger.error(f"❌ Rhubarb no encontrado en: {rhubarb_exe}")
        return None

    try:
        # Ejecutar Rhubarb
        cmd = [
            str(rhubarb_exe),
            "-f", "json",  # Formato JSON
            "-o", str(output_path),  # Output file
            str(audio_path)  # Input audio
        ]

        logger.info(f"   Ejecutando: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info(f"✅ Lip sync generado: {output_path}")

        # Leer y retornar datos
        with open(output_path, 'r', encoding='utf-8') as f:
            visemas = json.load(f)

        return visemas

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error ejecutando Rhubarb: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


def combinar_animacion_lipsync(animacion_path, lipsync_data, output_path):
    """
    Combina animación corporal con datos de lip sync

    Args:
        animacion_path: Video/frames de animación corporal
        lipsync_data: Datos JSON de Rhubarb
        output_path: Video final con lip sync

    Returns:
        bool: True si exitoso
    """
    logger.info(f"🎨 Combinando animación + lip sync")

    # TODO: Implementar combinación
    # Esto requiere procesamiento de video/frames
    # Podría usar ffmpeg, opencv, pillow, etc.

    logger.info(f"   Animación: {animacion_path}")
    logger.info(f"   Lip sync data: {len(lipsync_data.get('mouthCues', []))} cues")
    logger.info(f"   Output: {output_path}")

    return True


def main():
    """Pipeline de animación completo"""
    logger.info("=" * 70)
    logger.info("🎬 PIPELINE DE ANIMACIÓN")
    logger.info("=" * 70)

    # Configuración
    VIDEO_ID = "001"
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output" / f"{VIDEO_ID}-20260904"

    logger.info(f"📁 Procesando Video: {VIDEO_ID}")
    logger.info(f"📂 Carpeta: {output_dir}")
    logger.info("")

    # 1. Analizar guión
    guion_path = output_dir / "guion.json"
    if not guion_path.exists():
        logger.error(f"❌ Guión no encontrado: {guion_path}")
        return False

    escenas = analizar_guion_expresiones(guion_path)
    logger.info(f"✅ Detectadas {len(escenas)} escenas")
    logger.info("")

    # 2. Por cada escena, generar animación
    for escena in escenas:
        logger.info(f"🎬 Escena {escena['indice'] + 1}:")
        logger.info(f"   Personaje: {escena['personaje']}")
        logger.info(f"   Expresión: {escena['expresion']}")

        # Ruta a imagen del personaje
        personajes_dir = base_dir / "assets" / "personajes_base"
        imagen_nombre = f"{escena['personaje']}_{escena['expresion']}.png"
        imagen_path = personajes_dir / imagen_nombre

        # Verificar si existe (puede ser .jfif también)
        if not imagen_path.exists():
            imagen_path = imagen_path.with_suffix('.jfif')

        if not imagen_path.exists():
            logger.warning(f"⚠️ Imagen no encontrada: {imagen_nombre}")
            # Intentar con base
            imagen_path = personajes_dir / f"{escena['personaje']}_base.png"
            if not imagen_path.exists():
                imagen_path = imagen_path.with_suffix('.jfif')

        logger.info(f"   Imagen: {imagen_path.name}")
        logger.info("")

    logger.info("=" * 70)
    logger.info("⏸️  Pipeline animación (placeholder - desarrollo en progreso)")
    logger.info("=" * 70)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
