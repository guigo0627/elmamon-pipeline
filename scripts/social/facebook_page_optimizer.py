#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Page Optimizer
Actualiza información y configuración de la página de Facebook
"""

import sys
import os
from pathlib import Path
import requests
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('fb_optimizer')


class FacebookPageOptimizer:
    """Optimizador de página de Facebook"""

    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.graph_api_url = "https://graph.facebook.com/v18.0"

    def update_page_info(self, about=None, description=None, website=None):
        """
        Actualiza información básica de la página

        Args:
            about: Descripción corta
            description: Descripción larga
            website: URL del sitio web

        Returns:
            bool: True si exitoso
        """
        logger.info("=" * 70)
        logger.info("📝 ACTUALIZANDO INFORMACIÓN DE PÁGINA")
        logger.info("=" * 70)

        url = f"{self.graph_api_url}/{self.page_id}"

        params = {
            'access_token': self.access_token
        }

        if about:
            params['about'] = about
            logger.info(f"✏️  About: {about[:50]}...")

        if description:
            params['description'] = description
            logger.info(f"📄 Description: {description[:50]}...")

        if website:
            params['website'] = website
            logger.info(f"🔗 Website: {website}")

        try:
            response = requests.post(url, params=params)

            if response.status_code == 200:
                logger.info("✅ Información actualizada")
                return True
            else:
                logger.error(f"❌ Error: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False

    def upload_profile_picture(self, image_path):
        """
        Sube foto de perfil

        Args:
            image_path: Path a la imagen (320x320px recomendado)

        Returns:
            bool: True si exitoso
        """
        image_path = Path(image_path)

        if not image_path.exists():
            logger.error(f"❌ Imagen no encontrada: {image_path}")
            return False

        logger.info(f"📷 Subiendo foto de perfil: {image_path.name}")

        url = f"{self.graph_api_url}/{self.page_id}/picture"

        params = {
            'access_token': self.access_token
        }

        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = requests.post(url, params=params, files=files)

            if response.status_code == 200:
                logger.info("✅ Foto de perfil actualizada")
                return True
            else:
                logger.error(f"❌ Error: {response.text}")
                return False

    def upload_cover_photo(self, image_path):
        """
        Sube foto de portada

        Args:
            image_path: Path a la imagen (820x312px recomendado)

        Returns:
            bool: True si exitoso
        """
        image_path = Path(image_path)

        if not image_path.exists():
            logger.error(f"❌ Imagen no encontrada: {image_path}")
            return False

        logger.info(f"🖼️  Subiendo portada: {image_path.name}")

        url = f"{self.graph_api_url}/{self.page_id}/photos"

        params = {
            'access_token': self.access_token,
            'is_cover_photo': True
        }

        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = requests.post(url, params=params, files=files)

            if response.status_code == 200:
                logger.info("✅ Portada actualizada")
                return True
            else:
                logger.error(f"❌ Error: {response.text}")
                return False

    def get_page_info(self):
        """
        Obtiene información actual de la página

        Returns:
            dict: Información de la página
        """
        url = f"{self.graph_api_url}/{self.page_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'name,about,description,category,fan_count,website,username'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            logger.info("=" * 70)
            logger.info("📊 INFORMACIÓN ACTUAL DE LA PÁGINA")
            logger.info("=" * 70)
            logger.info(f"📛 Nombre: {data.get('name')}")
            logger.info(f"👥 Seguidores: {data.get('fan_count', 0):,}")
            logger.info(f"📝 About: {data.get('about', 'No configurado')}")
            logger.info(f"🏷️  Categoría: {data.get('category')}")
            logger.info(f"@️  Username: @{data.get('username', 'No configurado')}")

            return data
        else:
            logger.error(f"❌ Error obteniendo info: {response.text}")
            return None


def main():
    """Optimizar página con configuración recomendada"""
    # Configuración
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', 'TU_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', 'TU_ACCESS_TOKEN')

    if PAGE_ID == 'TU_PAGE_ID' or ACCESS_TOKEN == 'TU_ACCESS_TOKEN':
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN")
        return False

    optimizer = FacebookPageOptimizer(PAGE_ID, ACCESS_TOKEN)

    # Obtener info actual
    current_info = optimizer.get_page_info()

    if not current_info:
        return False

    # Actualizar información según estrategia SEO
    ABOUT = "Videos cómicos de situaciones cotidianas que todos vivimos 😂 Contenido original con animación. ¡Síguenos para reírte con escenas de la vida real! #Comedia #SituacionesCotidianas"

    DESCRIPTION = """Bienvenidos a ElMamón - tu dosis diaria de humor basado en situaciones reales.

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
    success = optimizer.update_page_info(
        about=ABOUT,
        description=DESCRIPTION
    )

    if success:
        logger.info("\n✅ Página optimizada según estrategia SEO")
        logger.info("📖 Ver docs/FACEBOOK_SEO_STRATEGY.md para más detalles")
        return True
    else:
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
