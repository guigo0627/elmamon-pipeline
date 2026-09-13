#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Page Analyzer
Analiza métricas, engagement y audiencia de una página de Facebook
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('page_analyzer')


class FacebookPageAnalyzer:
    """Analizador de página de Facebook"""

    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.graph_api_url = "https://graph.facebook.com/v18.0"

    def get_page_info(self):
        """Obtiene información básica de la página"""
        url = f"{self.graph_api_url}/{self.page_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'id,name,username,about,category,fan_count,followers_count,link,website,phone,emails,location'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error obteniendo info: {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None

    def get_page_insights(self, metrics, period='day', since_days=30):
        """
        Obtiene insights de la página

        Args:
            metrics: Lista de métricas a obtener
            period: Período ('day', 'week', 'days_28')
            since_days: Días hacia atrás para obtener datos
        """
        url = f"{self.graph_api_url}/{self.page_id}/insights"

        since = int((datetime.now() - timedelta(days=since_days)).timestamp())
        until = int(datetime.now().timestamp())

        params = {
            'access_token': self.access_token,
            'metric': ','.join(metrics),
            'period': period,
            'since': since,
            'until': until
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.warning(f"⚠️  No se pudieron obtener insights: {response.text}")
                return []
        except Exception as e:
            logger.warning(f"⚠️  Error obteniendo insights: {e}")
            return []

    def get_posts(self, limit=25):
        """Obtiene posts recientes de la página"""
        url = f"{self.graph_api_url}/{self.page_id}/posts"

        params = {
            'access_token': self.access_token,
            'fields': 'id,message,created_time,type,permalink_url,shares,reactions.summary(true),comments.summary(true)',
            'limit': limit
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.warning(f"⚠️  No se pudieron obtener posts: {response.text}")
                return []
        except Exception as e:
            logger.warning(f"⚠️  Error obteniendo posts: {e}")
            return []

    def calculate_engagement_rate(self, posts):
        """Calcula engagement rate promedio de los posts"""
        if not posts:
            return 0

        total_engagement = 0
        total_posts = len(posts)

        for post in posts:
            reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0)

            engagement = reactions + comments + shares
            total_engagement += engagement

        return total_engagement / total_posts if total_posts > 0 else 0

    def analyze_best_posting_times(self, posts):
        """Analiza mejores horarios de publicación basado en engagement"""
        if not posts:
            return {}

        hours_engagement = {}

        for post in posts:
            created_time = post.get('created_time')
            if not created_time:
                continue

            # Parse timestamp
            dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            hour = dt.hour

            # Calcular engagement
            reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0)
            engagement = reactions + comments + shares

            if hour not in hours_engagement:
                hours_engagement[hour] = {'total': 0, 'count': 0}

            hours_engagement[hour]['total'] += engagement
            hours_engagement[hour]['count'] += 1

        # Calcular promedio por hora
        hours_avg = {}
        for hour, data in hours_engagement.items():
            hours_avg[hour] = data['total'] / data['count'] if data['count'] > 0 else 0

        # Ordenar por engagement
        sorted_hours = sorted(hours_avg.items(), key=lambda x: x[1], reverse=True)

        return sorted_hours[:5]  # Top 5 horarios

    def analyze_content_performance(self, posts):
        """Analiza qué tipo de contenido funciona mejor"""
        if not posts:
            return {}

        type_performance = {}

        for post in posts:
            post_type = post.get('type', 'status')

            reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0)
            engagement = reactions + comments + shares

            if post_type not in type_performance:
                type_performance[post_type] = {'total': 0, 'count': 0, 'posts': []}

            type_performance[post_type]['total'] += engagement
            type_performance[post_type]['count'] += 1
            type_performance[post_type]['posts'].append({
                'message': post.get('message', '')[:50] + '...' if post.get('message') else 'Sin texto',
                'engagement': engagement,
                'url': post.get('permalink_url')
            })

        # Calcular promedio por tipo
        for post_type, data in type_performance.items():
            data['avg'] = data['total'] / data['count'] if data['count'] > 0 else 0

        return type_performance

    def generate_report(self):
        """Genera reporte completo de análisis"""
        logger.info("=" * 70)
        logger.info("📊 ANÁLISIS DE PÁGINA DE FACEBOOK")
        logger.info("=" * 70)
        logger.info("")

        # 1. Información básica
        logger.info("📋 INFORMACIÓN BÁSICA:")
        page_info = self.get_page_info()

        if page_info:
            logger.info(f"   🏷️  Nombre: {page_info.get('name')}")
            logger.info(f"   🆔 ID: {page_info.get('id')}")
            logger.info(f"   👤 Username: @{page_info.get('username', 'N/A')}")
            logger.info(f"   📁 Categoría: {page_info.get('category')}")
            logger.info(f"   👥 Fans: {page_info.get('fan_count', 0):,}")
            logger.info(f"   👥 Seguidores: {page_info.get('followers_count', 0):,}")
            logger.info(f"   🔗 Link: {page_info.get('link')}")

            if page_info.get('about'):
                logger.info(f"   ℹ️  Descripción: {page_info.get('about')[:100]}...")
        else:
            logger.warning("⚠️  No se pudo obtener información básica")

        logger.info("")

        # 2. Posts recientes
        logger.info("📝 POSTS RECIENTES (últimos 25):")
        posts = self.get_posts(limit=25)
        avg_engagement = 0  # Inicializar

        if posts:
            logger.info(f"   ✅ {len(posts)} posts encontrados")

            # Calcular engagement promedio
            avg_engagement = self.calculate_engagement_rate(posts)
            logger.info(f"   📊 Engagement promedio: {avg_engagement:.1f} interacciones/post")

            # Mejores posts
            logger.info("")
            logger.info("   🏆 TOP 5 POSTS:")
            sorted_posts = sorted(posts, key=lambda x: (
                x.get('reactions', {}).get('summary', {}).get('total_count', 0) +
                x.get('comments', {}).get('summary', {}).get('total_count', 0) +
                x.get('shares', {}).get('count', 0)
            ), reverse=True)[:5]

            for i, post in enumerate(sorted_posts, 1):
                reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = post.get('shares', {}).get('count', 0)
                total = reactions + comments + shares

                message = post.get('message', 'Sin texto')[:60]
                logger.info(f"      {i}. {message}...")
                logger.info(f"         💚 {reactions} | 💬 {comments} | 🔄 {shares} | 📊 Total: {total}")
                logger.info(f"         🔗 {post.get('permalink_url')}")
                logger.info("")

        else:
            logger.warning("   ⚠️  No se encontraron posts recientes")

        logger.info("")

        # 3. Mejores horarios
        logger.info("⏰ MEJORES HORARIOS DE PUBLICACIÓN:")
        best_times = self.analyze_best_posting_times(posts)

        if best_times:
            for hour, avg_eng in best_times:
                logger.info(f"   🕐 {hour:02d}:00 - Engagement promedio: {avg_eng:.1f}")
        else:
            logger.warning("   ⚠️  No hay suficientes datos para determinar mejores horarios")

        logger.info("")

        # 4. Análisis de contenido
        logger.info("📊 ANÁLISIS POR TIPO DE CONTENIDO:")
        content_perf = self.analyze_content_performance(posts)

        if content_perf:
            sorted_types = sorted(content_perf.items(), key=lambda x: x[1]['avg'], reverse=True)

            for content_type, data in sorted_types:
                logger.info(f"   📌 {content_type.upper()}:")
                logger.info(f"      Posts: {data['count']}")
                logger.info(f"      Engagement promedio: {data['avg']:.1f}")
        else:
            logger.warning("   ⚠️  No hay suficientes datos para análisis de contenido")

        logger.info("")

        # 5. Insights de la página (si están disponibles)
        logger.info("📈 INSIGHTS DE LA PÁGINA:")

        metrics = [
            'page_impressions',
            'page_engaged_users',
            'page_post_engagements',
            'page_video_views'
        ]

        insights = self.get_page_insights(metrics, period='day', since_days=7)

        if insights:
            for metric_data in insights:
                metric_name = metric_data.get('name')
                values = metric_data.get('values', [])

                if values:
                    total = sum(v.get('value', 0) for v in values)
                    avg = total / len(values)

                    logger.info(f"   📊 {metric_name}: {avg:.0f} (promedio últimos 7 días)")
        else:
            logger.warning("   ⚠️  No hay insights disponibles (requiere permisos adicionales)")

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ ANÁLISIS COMPLETADO")
        logger.info("=" * 70)

        return {
            'page_info': page_info,
            'posts_count': len(posts),
            'avg_engagement': avg_engagement,
            'best_times': best_times,
            'content_performance': content_perf
        }


def main():
    """Ejecuta análisis de la página"""
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not PAGE_ID or not ACCESS_TOKEN:
        logger.error("❌ Faltan credenciales de Facebook")
        logger.info("   Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en .env")
        return False

    analyzer = FacebookPageAnalyzer(PAGE_ID, ACCESS_TOKEN)
    result = analyzer.generate_report()

    return result is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
