#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduled Publisher - Publicación programada estratégica
Programa videos para horarios óptimos de engagement
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import time

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('scheduled_publisher')

# Import facebook publisher (mismo directorio)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "facebook_publisher",
    Path(__file__).parent / "facebook_publisher.py"
)
fb_publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fb_publisher)
FacebookPublisher = fb_publisher.FacebookPublisher


# Horarios estratégicos por día de la semana
OPTIMAL_POSTING_TIMES = {
    'monday': ['09:00', '13:00', '19:00'],      # Lunes
    'tuesday': ['09:00', '13:00', '19:00'],     # Martes
    'wednesday': ['09:00', '13:00', '19:00'],   # Miércoles
    'thursday': ['09:00', '13:00', '19:00'],    # Jueves
    'friday': ['09:00', '13:00', '20:00'],      # Viernes
    'saturday': ['11:00', '15:00', '20:00'],    # Sábado
    'sunday': ['11:00', '15:00', '20:00']       # Domingo
}


def parse_time_str(time_str, target_date=None):
    """
    Convierte string de hora a timestamp Unix

    Args:
        time_str: Hora en formato "HH:MM" (ej: "13:00")
        target_date: Fecha objetivo (opcional, default: hoy)

    Returns:
        int: Timestamp Unix
    """
    if target_date is None:
        target_date = datetime.now()

    hour, minute = map(int, time_str.split(':'))

    # Crear datetime con la hora especificada
    scheduled_dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Si la hora ya pasó hoy, programar para mañana
    if scheduled_dt < datetime.now():
        scheduled_dt += timedelta(days=1)
        logger.info(f"⏰ Hora ya pasó hoy, programando para mañana: {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")

    return int(scheduled_dt.timestamp())


def get_next_optimal_time(custom_time=None):
    """
    Obtiene el siguiente horario óptimo para publicar

    Args:
        custom_time: Hora personalizada en formato "HH:MM" (opcional)

    Returns:
        int: Timestamp Unix del siguiente horario óptimo
    """
    now = datetime.now()

    # Si hay hora personalizada, usarla
    if custom_time:
        logger.info(f"🕐 Usando hora personalizada: {custom_time}")
        return parse_time_str(custom_time, now)

    # Obtener horarios óptimos para hoy
    day_name = now.strftime('%A').lower()
    optimal_times = OPTIMAL_POSTING_TIMES.get(day_name, ['13:00', '19:00'])

    logger.info(f"📅 Hoy es {day_name.capitalize()}")
    logger.info(f"⏰ Horarios óptimos: {', '.join(optimal_times)}")

    # Buscar el siguiente horario disponible
    for time_str in optimal_times:
        timestamp = parse_time_str(time_str, now)
        scheduled_dt = datetime.fromtimestamp(timestamp)

        if scheduled_dt > now:
            logger.info(f"✅ Siguiente horario óptimo: {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")
            return timestamp

    # Si no hay horarios disponibles hoy, tomar el primero de mañana
    tomorrow = now + timedelta(days=1)
    tomorrow_day = tomorrow.strftime('%A').lower()
    tomorrow_times = OPTIMAL_POSTING_TIMES.get(tomorrow_day, ['13:00'])
    timestamp = parse_time_str(tomorrow_times[0], tomorrow)

    scheduled_dt = datetime.fromtimestamp(timestamp)
    logger.info(f"✅ Próximo horario (mañana): {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")

    return timestamp


def schedule_video_publication(video_path, title, description, tags=None, scheduled_time=None):
    """
    Programa un video para publicación futura

    Args:
        video_path: Path al video
        title: Título del video
        description: Descripción corta
        tags: Lista de hashtags
        scheduled_time: Hora personalizada "HH:MM" o None para óptimo automático

    Returns:
        dict: Respuesta de Facebook
    """
    # Cargar credenciales
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not PAGE_ID or not ACCESS_TOKEN:
        logger.error("❌ Faltan credenciales de Facebook")
        logger.info("   Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en .env")
        return None

    # Calcular timestamp
    timestamp = get_next_optimal_time(scheduled_time)
    scheduled_dt = datetime.fromtimestamp(timestamp)

    logger.info("")
    logger.info("=" * 70)
    logger.info("📅 PROGRAMANDO PUBLICACIÓN")
    logger.info("=" * 70)
    logger.info(f"📹 Video: {Path(video_path).name}")
    logger.info(f"📝 Título: {title}")
    logger.info(f"🕐 Fecha/Hora: {scheduled_dt.strftime('%Y-%m-%d %H:%M %p')}")
    logger.info(f"⏰ Timestamp: {timestamp}")
    logger.info("")

    # Confirmar
    time_until = scheduled_dt - datetime.now()
    hours = time_until.total_seconds() / 3600

    if hours < 0:
        logger.error("❌ La hora programada ya pasó")
        return None

    logger.info(f"⏳ Tiempo hasta publicación: {hours:.1f} horas")
    logger.info("")

    # Crear publicador
    publisher = FacebookPublisher(PAGE_ID, ACCESS_TOKEN)

    # Programar video
    result = publisher.schedule_video(
        video_path,
        title=title,
        description=description,
        scheduled_time=timestamp,
        tags=tags,
        use_cta_template=True
    )

    if result:
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ VIDEO PROGRAMADO EXITOSAMENTE")
        logger.info("=" * 70)
        logger.info(f"🆔 Video ID: {result.get('id')}")
        logger.info(f"📅 Se publicará: {scheduled_dt.strftime('%Y-%m-%d %H:%M %p')}")
        logger.info("")

    return result


def main():
    """Programa video más reciente con horario óptimo o personalizado"""
    import argparse

    parser = argparse.ArgumentParser(description='Programa video para publicación')
    parser.add_argument('--time', type=str, help='Hora personalizada (HH:MM, ej: 13:00)')
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent.parent
    output_base = base_dir / "output"

    # Buscar video más reciente
    video_dirs = sorted([d for d in output_base.glob("*-*") if d.is_dir()], reverse=True)

    if not video_dirs:
        logger.error(f"❌ No se encontraron videos en {output_base}")
        return False

    latest_dir = video_dirs[0]
    video_path = latest_dir / "scene_00s_titled_final.mp4"
    animation_plan_path = latest_dir / "animation_plan.json"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        return False

    # Cargar título y descripción
    title = "Situaciones Cotidianas 😅"
    short_desc = "¿Les pasa o solo a mí? 😂"
    tags = ["Comedia", "Humor", "SituacionesCotidianas", "AsíEs", "Pareja", "Viral"]

    if animation_plan_path.exists():
        try:
            with open(animation_plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
                title = plan['analysis'].get('recommended_title', title)
                hooks = plan['analysis'].get('hook_titles', [])
                if hooks:
                    short_desc = hooks[0] if len(hooks[0]) < 100 else hooks[0][:97] + "..."
        except Exception as e:
            logger.warning(f"⚠️  No se pudo leer animation_plan.json: {e}")

    # Programar publicación
    result = schedule_video_publication(
        video_path,
        title=title,
        description=short_desc,
        tags=tags,
        scheduled_time=args.time  # None = automático, o "HH:MM" = personalizado
    )

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
