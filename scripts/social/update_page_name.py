#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualizar nombre y descripción de página de Facebook
"""

import sys
import os
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('page_update')


def update_page_name_and_info(page_id, access_token, name, about, description):
    """
    Actualiza nombre y descripción de la página

    Args:
        page_id: ID de la página
        access_token: Access token con permisos pages_manage_metadata
        name: Nuevo nombre de la página
        about: Descripción corta
        description: Descripción larga

    Returns:
        bool: True si exitoso
    """
    graph_api_url = "https://graph.facebook.com/v18.0"
    url = f"{graph_api_url}/{page_id}"

    logger.info("=" * 70)
    logger.info("🔧 ACTUALIZANDO PÁGINA DE FACEBOOK")
    logger.info("=" * 70)

    # Parámetros a actualizar
    params = {
        'access_token': access_token,
        'name': name,
        'about': about,
        'description': description
    }

    logger.info(f"📝 Nuevo nombre: {name}")
    logger.info(f"📝 About: {about[:60]}...")
    logger.info(f"📝 Description: {description[:60]}...")

    try:
        response = requests.post(url, params=params)

        if response.status_code == 200:
            result = response.json()
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ PÁGINA ACTUALIZADA EXITOSAMENTE")
            logger.info("=" * 70)
            logger.info(f"🎉 Nombre cambiado a: {name}")
            logger.info("⚠️  Nota: El cambio puede tardar unos minutos en reflejarse")
            return True
        else:
            error_data = response.json()
            logger.error("=" * 70)
            logger.error("❌ ERROR AL ACTUALIZAR")
            logger.error("=" * 70)
            logger.error(f"Código: {response.status_code}")
            logger.error(f"Error: {error_data.get('error', {}).get('message', 'Unknown')}")

            # Mensajes de ayuda según el error
            error_message = error_data.get('error', {}).get('message', '')
            if 'name' in error_message.lower():
                logger.warning("")
                logger.warning("💡 POSIBLES RAZONES:")
                logger.warning("   - El nombre es muy similar al actual")
                logger.warning("   - Has cambiado el nombre recientemente")
                logger.warning("   - El nombre está en uso por otra página")
                logger.warning("   - Facebook requiere revisión manual del cambio")
                logger.warning("")
                logger.warning("🔧 SOLUCIÓN:")
                logger.warning("   - Intenta cambiar el nombre manualmente desde la página")
                logger.warning("   - Espera 7-14 días antes de cambiarlo nuevamente")

            return False

    except Exception as e:
        logger.error(f"❌ Error de conexión: {e}")
        return False


def main():
    """Actualizar página a 'Vida Cotidiana'"""
    # Cargar configuración
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not PAGE_ID or not ACCESS_TOKEN:
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en .env")
        return False

    # Nueva configuración
    NEW_NAME = "Vida Cotidiana"

    ABOUT = "Videos cómicos de situaciones cotidianas que todos vivimos 😂 Contenido original con animación. ¡Síguenos para reírte con escenas de la vida real! #Comedia #SituacionesCotidianas"

    DESCRIPTION = """Bienvenidos a Vida Cotidiana - tu dosis diaria de humor basado en situaciones reales.

🎬 ¿Qué encontrarás aquí?
• Videos cortos de situaciones cotidianas
• Humor de pareja y familia
• Escenas que todos hemos vivido
• Animación original y única

📹 Nuevo contenido cada semana
👥 Únete a nuestra comunidad
💬 Comparte tus propias situaciones

¡Dale like y comparte para más videos! 😄

#Comedia #Humor #SituacionesCotidianas #VideosCortos #Animacion #Pareja #Familia"""

    # Actualizar
    success = update_page_name_and_info(
        PAGE_ID,
        ACCESS_TOKEN,
        NEW_NAME,
        ABOUT,
        DESCRIPTION
    )

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
