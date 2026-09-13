#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualizar categoría de página de Facebook
"""

import sys
import os
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('category_update')


def update_page_category(page_id, access_token, category_enum):
    """
    Actualiza la categoría de la página

    Args:
        page_id: ID de la página
        access_token: Access token con permisos pages_manage_metadata
        category_enum: Categoría (ej: 'ENTERTAINMENT', 'COMEDIAN', etc.)

    Returns:
        bool: True si exitoso
    """
    graph_api_url = "https://graph.facebook.com/v18.0"
    url = f"{graph_api_url}/{page_id}"

    logger.info("=" * 70)
    logger.info("🏷️  ACTUALIZANDO CATEGORÍA DE PÁGINA")
    logger.info("=" * 70)

    params = {
        'access_token': access_token,
        'category_enum': category_enum
    }

    logger.info(f"📝 Nueva categoría: {category_enum}")

    try:
        response = requests.post(url, params=params)

        if response.status_code == 200:
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ CATEGORÍA ACTUALIZADA")
            logger.info("=" * 70)
            logger.info(f"🎉 Categoría cambiada a: {category_enum}")
            return True
        else:
            error_data = response.json()
            logger.error("=" * 70)
            logger.error("❌ ERROR AL ACTUALIZAR CATEGORÍA")
            logger.error("=" * 70)
            logger.error(f"Código: {response.status_code}")
            logger.error(f"Error: {error_data.get('error', {}).get('message', 'Unknown')}")

            logger.warning("")
            logger.warning("💡 POSIBLES RAZONES:")
            logger.warning("   - Categoría no válida o no disponible")
            logger.warning("   - Se necesita cambiar manualmente desde la página")
            logger.warning("")
            logger.warning("🔧 CATEGORÍAS COMUNES:")
            logger.warning("   - ENTERTAINMENT (Entretenimiento)")
            logger.warning("   - COMEDIAN (Comediante)")
            logger.warning("   - VIDEO_CREATOR (Creador de videos)")
            logger.warning("   - CONTENT_AND_APPS (Contenido y aplicaciones)")

            return False

    except Exception as e:
        logger.error(f"❌ Error de conexión: {e}")
        return False


def main():
    """Actualizar categoría a Entretenimiento"""
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not PAGE_ID or not ACCESS_TOKEN:
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en .env")
        return False

    # Intentar con diferentes categorías relacionadas
    categories = [
        'ENTERTAINMENT',  # Entretenimiento
        'COMEDIAN',       # Comediante
        'VIDEO_CREATOR',  # Creador de videos
    ]

    for category in categories:
        logger.info(f"\n🔄 Intentando con: {category}")
        if update_page_category(PAGE_ID, ACCESS_TOKEN, category):
            return True
        logger.info("⏭️  Probando siguiente categoría...")

    logger.warning("")
    logger.warning("=" * 70)
    logger.warning("⚠️  NO SE PUDO ACTUALIZAR VÍA API")
    logger.warning("=" * 70)
    logger.warning("Debes cambiar la categoría manualmente desde la página:")
    logger.warning("1. Ir a Configuración → Información de la página")
    logger.warning("2. Buscar 'Categoría'")
    logger.warning("3. Seleccionar: Entretenimiento / Página de comedia")

    return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
