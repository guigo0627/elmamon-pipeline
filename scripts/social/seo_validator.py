#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Validator - Pre-publicación
Valida título, descripción, hashtags y características del video
"""

import sys
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('seo_validator')

try:
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


class SEOValidator:
    """Validador SEO para videos de Facebook/Instagram"""

    # Rangos óptimos para Facebook Reels
    OPTIMAL_TITLE_LENGTH = (30, 60)  # caracteres
    OPTIMAL_DESC_LENGTH = (100, 300)  # caracteres
    OPTIMAL_HASHTAGS = (5, 8)  # cantidad
    OPTIMAL_VIDEO_DURATION = (15, 60)  # segundos
    MAX_FILE_SIZE_MB = 100  # MB
    OPTIMAL_ASPECT_RATIO = (9, 16)  # vertical

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []

    def validate_title(self, title):
        """Valida longitud y calidad del título"""
        length = len(title)

        if length < self.OPTIMAL_TITLE_LENGTH[0]:
            self.warnings.append(f"📝 Título corto ({length} chars). Óptimo: {self.OPTIMAL_TITLE_LENGTH[0]}-{self.OPTIMAL_TITLE_LENGTH[1]}")
        elif length > self.OPTIMAL_TITLE_LENGTH[1]:
            self.warnings.append(f"📝 Título largo ({length} chars). Óptimo: {self.OPTIMAL_TITLE_LENGTH[0]}-{self.OPTIMAL_TITLE_LENGTH[1]}")
        else:
            self.passed.append(f"✅ Título óptimo ({length} chars)")

        # Verificar emojis (buenos para engagement)
        has_emoji = any(ord(char) > 127 for char in title)
        if has_emoji:
            self.passed.append("✅ Título incluye emoji (aumenta engagement)")
        else:
            self.warnings.append("⚠️  Título sin emoji (considera agregar uno)")

    def validate_description(self, description):
        """Valida descripción y CTAs"""
        length = len(description)

        if length < self.OPTIMAL_DESC_LENGTH[0]:
            self.warnings.append(f"📄 Descripción corta ({length} chars). Óptimo: {self.OPTIMAL_DESC_LENGTH[0]}-{self.OPTIMAL_DESC_LENGTH[1]}")
        elif length > self.OPTIMAL_DESC_LENGTH[1]:
            self.warnings.append(f"📄 Descripción larga ({length} chars). Óptimo: {self.OPTIMAL_DESC_LENGTH[0]}-{self.OPTIMAL_DESC_LENGTH[1]}")
        else:
            self.passed.append(f"✅ Descripción óptima ({length} chars)")

        # Verificar CTAs
        cta_keywords = ['like', 'comparte', 'comenta', 'etiqueta', 'sigue', 'comparte']
        has_cta = any(keyword in description.lower() for keyword in cta_keywords)

        if has_cta:
            self.passed.append("✅ Descripción incluye CTA")
        else:
            self.issues.append("❌ Descripción sin CTA (call-to-action)")

    def validate_hashtags(self, description):
        """Valida número y calidad de hashtags"""
        hashtags = [word for word in description.split() if word.startswith('#')]
        count = len(hashtags)

        if count < self.OPTIMAL_HASHTAGS[0]:
            self.warnings.append(f"🏷️  Pocos hashtags ({count}). Óptimo: {self.OPTIMAL_HASHTAGS[0]}-{self.OPTIMAL_HASHTAGS[1]}")
        elif count > self.OPTIMAL_HASHTAGS[1]:
            self.warnings.append(f"🏷️  Muchos hashtags ({count}). Óptimo: {self.OPTIMAL_HASHTAGS[0]}-{self.OPTIMAL_HASHTAGS[1]}")
        else:
            self.passed.append(f"✅ Hashtags óptimos ({count})")

        # Verificar longitud de hashtags
        for tag in hashtags:
            if len(tag) > 30:
                self.warnings.append(f"⚠️  Hashtag muy largo: {tag[:30]}...")

    def validate_video(self, video_path):
        """Valida características técnicas del video"""
        if not MOVIEPY_AVAILABLE:
            self.warnings.append("⚠️  MoviePy no disponible - validación técnica omitida")
            return

        video_path = Path(video_path)

        if not video_path.exists():
            self.issues.append(f"❌ Video no encontrado: {video_path}")
            return

        # Tamaño del archivo
        size_mb = video_path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            self.issues.append(f"❌ Video muy grande ({size_mb:.1f} MB). Máximo: {self.MAX_FILE_SIZE_MB} MB")
        else:
            self.passed.append(f"✅ Tamaño adecuado ({size_mb:.1f} MB)")

        # Características del video
        try:
            video = VideoFileClip(str(video_path))

            # Duración
            duration = video.duration
            if duration < self.OPTIMAL_VIDEO_DURATION[0]:
                self.warnings.append(f"⏱️  Video corto ({duration:.1f}s). Óptimo: {self.OPTIMAL_VIDEO_DURATION[0]}-{self.OPTIMAL_VIDEO_DURATION[1]}s")
            elif duration > self.OPTIMAL_VIDEO_DURATION[1]:
                self.warnings.append(f"⏱️  Video largo ({duration:.1f}s). Óptimo: {self.OPTIMAL_VIDEO_DURATION[0]}-{self.OPTIMAL_VIDEO_DURATION[1]}s")
            else:
                self.passed.append(f"✅ Duración óptima ({duration:.1f}s)")

            # Relación de aspecto
            width, height = video.size
            aspect_ratio = (width, height)

            if aspect_ratio == self.OPTIMAL_ASPECT_RATIO or (width, height) == (1080, 1920):
                self.passed.append(f"✅ Formato vertical correcto ({width}x{height})")
            else:
                self.warnings.append(f"⚠️  Formato no óptimo ({width}x{height}). Óptimo: 1080x1920 (9:16)")

            # Audio
            if video.audio is None:
                self.issues.append("❌ Video sin audio")
            else:
                self.passed.append("✅ Video tiene audio")

            video.close()

        except Exception as e:
            self.warnings.append(f"⚠️  Error validando video: {e}")

    def generate_report(self):
        """Genera reporte de validación"""
        logger.info("=" * 70)
        logger.info("🔍 REPORTE DE VALIDACIÓN SEO")
        logger.info("=" * 70)
        logger.info("")

        # Calcular score
        total_checks = len(self.passed) + len(self.warnings) + len(self.issues)
        score = (len(self.passed) / total_checks * 100) if total_checks > 0 else 0

        # Mostrar resultados
        if self.passed:
            logger.info("✅ APROBADO:")
            for item in self.passed:
                logger.info(f"   {item}")
            logger.info("")

        if self.warnings:
            logger.info("⚠️  ADVERTENCIAS:")
            for item in self.warnings:
                logger.info(f"   {item}")
            logger.info("")

        if self.issues:
            logger.info("❌ PROBLEMAS:")
            for item in self.issues:
                logger.info(f"   {item}")
            logger.info("")

        # Score final
        logger.info("=" * 70)
        if score >= 80:
            logger.info(f"🎉 SCORE SEO: {score:.0f}% - EXCELENTE")
        elif score >= 60:
            logger.info(f"👍 SCORE SEO: {score:.0f}% - BUENO")
        else:
            logger.info(f"⚠️  SCORE SEO: {score:.0f}% - MEJORAR")
        logger.info("=" * 70)

        return {
            'score': score,
            'passed': len(self.passed),
            'warnings': len(self.warnings),
            'issues': len(self.issues),
            'ready_to_publish': len(self.issues) == 0
        }


def validate_video_seo(video_path, title, description):
    """
    Valida SEO de un video antes de publicar

    Args:
        video_path: Path al video
        title: Título del video
        description: Descripción completa (con CTAs y hashtags)

    Returns:
        dict: Reporte de validación
    """
    validator = SEOValidator()

    logger.info(f"📹 Video: {Path(video_path).name}")
    logger.info(f"📝 Título: {title}")
    logger.info(f"📄 Descripción: {description[:100]}...")
    logger.info("")

    # Validaciones
    validator.validate_title(title)
    validator.validate_description(description)
    validator.validate_hashtags(description)
    validator.validate_video(video_path)

    # Generar reporte
    return validator.generate_report()


def main():
    """Test del validador con video más reciente"""
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

    # Cargar título
    title = "Video de prueba"
    description = "Descripción de prueba"

    if animation_plan_path.exists():
        try:
            with open(animation_plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
                title = plan['analysis'].get('recommended_title', title)

                # Generar descripción con CTAs
                hooks = plan['analysis'].get('hook_titles', [])
                short_desc = hooks[0] if hooks else title

                # Simular plantilla de CTAs
                description = f"""{short_desc}

👉 Dale like y comparte
💬 Cuéntanos en los comentarios
🔄 Etiqueta a quien le pasa

#Comedia #Humor #SituacionesCotidianas #AsíEs #Pareja #Viral"""
        except Exception as e:
            logger.warning(f"⚠️  Error leyendo animation_plan: {e}")

    # Validar
    result = validate_video_seo(video_path, title, description)

    return result['ready_to_publish']


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
