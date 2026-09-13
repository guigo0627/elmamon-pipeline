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

    def generate_post_description(self, short_description, tags=None):
        """
        Genera descripción con CTAs según estrategia de contenido

        Args:
            short_description: Descripción corta (1-2 líneas)
            tags: Lista de hashtags (opcional)

        Returns:
            str: Descripción formateada con CTAs
        """
        # Plantilla de CTAs - lenguaje coloquial y cercano
        cta_template = """
👉 Dale like y comparte
💬 Cuéntanos en los comentarios
🔄 Etiqueta a quien le pasa
"""

        # Hashtags por defecto si no se proporcionan
        if not tags:
            tags = ["Comedia", "Humor", "SituacionesCotidianas", "AsíEs", "Viral"]

        # Asegurar 5-8 hashtags (estrategia óptima)
        if len(tags) < 5:
            # Agregar hashtags genéricos
            default_tags = ["VideosCortos", "Animacion", "Pareja", "Familia"]
            tags.extend([t for t in default_tags if t not in tags])
            tags = tags[:8]  # Máximo 8
        elif len(tags) > 8:
            tags = tags[:8]  # Limitar a 8

        # Construir hashtags
        hashtags = " ".join([f"#{tag}" for tag in tags])

        # Descripción completa
        full_description = f"{short_description}\n{cta_template}\n{hashtags}"

        return full_description

    def upload_video(self, video_path, title, description, tags=None, use_cta_template=True):
        """
        Sube un video a Facebook

        Args:
            video_path: Path al video
            title: Título del video
            description: Descripción corta del video
            tags: Lista de hashtags (opcional)
            use_cta_template: Si True, usa plantilla con CTAs (default: True)

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

        # Construir descripción con CTAs si está habilitado
        if use_cta_template:
            full_description = self.generate_post_description(description, tags)
            logger.info(f"✅ Usando plantilla con CTAs y {len(tags) if tags else 5} hashtags")
        else:
            # Modo legacy: solo descripción + hashtags
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

    def schedule_video(self, video_path, title, description, scheduled_time, tags=None, use_cta_template=True):
        """
        Programa un video para publicación futura

        Args:
            video_path: Path al video
            title: Título del video
            description: Descripción corta
            scheduled_time: Timestamp Unix para publicación
            tags: Lista de hashtags
            use_cta_template: Si True, usa plantilla con CTAs (default: True)

        Returns:
            dict: Respuesta de Facebook
        """
        # Construir descripción con CTAs si está habilitado
        if use_cta_template:
            full_description = self.generate_post_description(description, tags)
        else:
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
    """Test del publicador con CTAs"""
    # IMPORTANTE: Configurar estas variables
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', 'TU_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', 'TU_ACCESS_TOKEN')

    if PAGE_ID == 'TU_PAGE_ID' or ACCESS_TOKEN == 'TU_ACCESS_TOKEN':
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN")
        logger.info("   Crear archivo .env con:")
        logger.info("   FACEBOOK_PAGE_ID=tu_page_id")
        logger.info("   FACEBOOK_ACCESS_TOKEN=tu_token")
        return False

    # Video a publicar (buscar el más reciente)
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "output"

    # Buscar carpetas de output ordenadas por fecha
    video_dirs = sorted([d for d in output_dir.glob("*-*") if d.is_dir()], reverse=True)

    if not video_dirs:
        logger.error(f"❌ No se encontraron videos en {output_dir}")
        return False

    # Tomar el video más reciente
    latest_dir = video_dirs[0]
    video_path = latest_dir / "scene_00s_titled_final.mp4"

    if not video_path.exists():
        logger.error(f"❌ Video no encontrado: {video_path}")
        logger.info(f"   Buscado en: {latest_dir}")
        return False

    # Intentar cargar título desde animation_plan.json
    animation_plan_path = latest_dir / "animation_plan.json"
    title = "Situaciones Cotidianas 😅"
    short_desc = "¿Les pasa o solo a mí? 😂"

    if animation_plan_path.exists():
        try:
            with open(animation_plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
                title = plan['analysis'].get('recommended_title', title)
                # Usar primer hook_title como descripción corta
                hooks = plan['analysis'].get('hook_titles', [])
                if hooks:
                    short_desc = hooks[0] if len(hooks[0]) < 100 else hooks[0][:97] + "..."
        except Exception as e:
            logger.warning(f"⚠️  No se pudo leer animation_plan.json: {e}")

    logger.info(f"🎬 Video encontrado: {latest_dir.name}")
    logger.info(f"📝 Título: {title}")
    logger.info(f"📄 Descripción: {short_desc}")

    # Crear publicador
    publisher = FacebookPublisher(PAGE_ID, ACCESS_TOKEN)

    # Publicar con plantilla de CTAs (use_cta_template=True por defecto)
    result = publisher.upload_video(
        video_path,
        title=title,
        description=short_desc,
        tags=["Comedia", "Humor", "SituacionesCotidianas", "AsíEs", "Pareja", "Viral"],
        use_cta_template=True  # ✅ Usa plantilla con CTAs
    )

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
