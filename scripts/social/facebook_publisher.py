#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Video Publisher
Publica videos automáticamente a una página de Facebook
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('facebook')


class FacebookPublisher:
    """Publicador de videos a Facebook"""

    def __init__(self, page_id, access_token):
        """
        Inicializar publicador

        Args:
            page_id: ID de la página de Facebook
            access_token: Token de acceso de la página
        """
        self.page_id = page_id
        self.access_token = access_token
        self.graph_api_url = "https://graph.facebook.com/v18.0"

    def upload_video(self, video_path, title, description, tags=None):
        """
        Sube un video a Facebook

        Args:
            video_path: Path al video
            title: Título del video
            description: Descripción del video
            tags: Lista de hashtags (opcional)

        Returns:
            dict: Respuesta de Facebook con video_id
        """
        video_path = Path(video_path)

        if not video_path.exists():
            logger.error(f"❌ Video no encontrado: {video_path}")
            return None

        logger.info("=" * 70)
        logger.info("📤 PUBLICANDO A FACEBOOK")
        logger.info("=" * 70)
        logger.info(f"📹 Video: {video_path.name}")
        logger.info(f"📝 Título: {title}")

        # Construir descripción con hashtags
        full_description = description
        if tags:
            hashtags = " ".join([f"#{tag}" for tag in tags])
            full_description = f"{description}\n\n{hashtags}"

        # Endpoint para subir video
        url = f"{self.graph_api_url}/{self.page_id}/videos"

        # Parámetros
        params = {
            'access_token': self.access_token,
            'title': title,
            'description': full_description,
        }

        try:
            # Abrir video en modo binario
            with open(video_path, 'rb') as video_file:
                files = {
                    'source': video_file
                }

                logger.info("⏳ Subiendo video... (esto puede tomar unos minutos)")

                # Hacer request
                response = requests.post(
                    url,
                    params=params,
                    files=files,
                    timeout=600  # 10 minutos timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    video_id = data.get('id')

                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("✅ VIDEO PUBLICADO")
                    logger.info("=" * 70)
                    logger.info(f"🆔 Video ID: {video_id}")
                    logger.info(f"🔗 URL: https://facebook.com/{video_id}")

                    return data
                else:
                    logger.error(f"❌ Error {response.status_code}: {response.text}")
                    return None

        except requests.Timeout:
            logger.error("❌ Timeout subiendo video (>10 min)")
            return None
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None

    def schedule_video(self, video_path, title, description, scheduled_time, tags=None):
        """
        Programa un video para publicación futura

        Args:
            video_path: Path al video
            title: Título del video
            description: Descripción
            scheduled_time: Timestamp Unix para publicación
            tags: Lista de hashtags

        Returns:
            dict: Respuesta de Facebook
        """
        # Construir descripción
        full_description = description
        if tags:
            hashtags = " ".join([f"#{tag}" for tag in tags])
            full_description = f"{description}\n\n{hashtags}"

        url = f"{self.graph_api_url}/{self.page_id}/videos"

        params = {
            'access_token': self.access_token,
            'title': title,
            'description': full_description,
            'scheduled_publish_time': scheduled_time,
            'published': False,  # No publicar inmediatamente
        }

        with open(video_path, 'rb') as video_file:
            files = {'source': video_file}
            response = requests.post(url, params=params, files=files, timeout=600)

            if response.status_code == 200:
                logger.info(f"✅ Video programado para: {datetime.fromtimestamp(scheduled_time)}")
                return response.json()
            else:
                logger.error(f"❌ Error: {response.text}")
                return None


def main():
    """Test del publicador"""
    # IMPORTANTE: Configurar estas variables
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', 'TU_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', 'TU_ACCESS_TOKEN')

    if PAGE_ID == 'TU_PAGE_ID' or ACCESS_TOKEN == 'TU_ACCESS_TOKEN':
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN")
        logger.info("   Crear archivo .env con:")
        logger.info("   FACEBOOK_PAGE_ID=tu_page_id")
        logger.info("   FACEBOOK_ACCESS_TOKEN=tu_token")
        return False

    # Video a publicar
    base_dir = Path(__file__).parent.parent.parent
    video_path = base_dir / "output" / "003-20260912" / "scene_00s_titled_final.mp4"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        return False

    # Crear publicador
    publisher = FacebookPublisher(PAGE_ID, ACCESS_TOKEN)

    # Publicar
    result = publisher.upload_video(
        video_path,
        title="Cuando mi esposa me pide perdón... 😅",
        description="Situaciones cotidianas que todos vivimos 😂",
        tags=["comedia", "pareja", "situaciones", "humor", "animacion"]
    )

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
