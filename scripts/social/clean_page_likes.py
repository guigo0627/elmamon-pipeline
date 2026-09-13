#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpiar "Me gusta" de la página
Permite ver y remover páginas que tu página sigue
"""

import sys
import os
from pathlib import Path
import requests
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('page_cleanup')


def get_page_likes(page_id, access_token):
    """
    Obtiene lista de páginas que tu página sigue

    Returns:
        list: Lista de páginas con {id, name}
    """
    graph_api_url = "https://graph.facebook.com/v18.0"
    url = f"{graph_api_url}/{page_id}/likes"

    params = {
        'access_token': access_token,
        'fields': 'id,name,category',
        'limit': 100  # Máximo por request
    }

    all_likes = []

    logger.info("🔍 Obteniendo páginas que sigues...")

    try:
        while url:
            response = requests.get(url, params=params)

            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"❌ Error: {error_data.get('error', {}).get('message', 'Unknown')}")
                return None

            data = response.json()
            likes = data.get('data', [])
            all_likes.extend(likes)

            # Siguiente página (si hay más)
            url = data.get('paging', {}).get('next')
            params = {}  # La URL ya tiene los params

        return all_likes

    except Exception as e:
        logger.error(f"❌ Error de conexión: {e}")
        return None


def unlike_page(page_id, access_token, liked_page_id):
    """
    Deja de seguir una página

    Args:
        page_id: ID de tu página
        access_token: Token de acceso
        liked_page_id: ID de la página a dejar de seguir

    Returns:
        bool: True si exitoso
    """
    graph_api_url = "https://graph.facebook.com/v18.0"
    url = f"{graph_api_url}/{page_id}/likes/{liked_page_id}"

    params = {
        'access_token': access_token
    }

    try:
        response = requests.delete(url, params=params)

        if response.status_code == 200:
            return True
        else:
            error_data = response.json()
            logger.error(f"❌ Error: {error_data.get('error', {}).get('message', 'Unknown')}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Limpiar likes de la página"""
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not PAGE_ID or not ACCESS_TOKEN:
        logger.error("❌ Configurar FACEBOOK_PAGE_ID y FACEBOOK_ACCESS_TOKEN en .env")
        return False

    logger.info("=" * 70)
    logger.info("🧹 LIMPIEZA DE PÁGINAS SEGUIDAS")
    logger.info("=" * 70)

    # Obtener lista de páginas
    likes = get_page_likes(PAGE_ID, ACCESS_TOKEN)

    if likes is None:
        logger.error("")
        logger.error("⚠️  NO SE PUDO OBTENER LA LISTA")
        logger.error("")
        logger.error("💡 POSIBLES RAZONES:")
        logger.error("   - Falta permiso: pages_read_engagement")
        logger.error("   - Token expirado")
        logger.error("")
        logger.error("🔧 SOLUCIÓN:")
        logger.error("   1. Ir a Graph API Explorer")
        logger.error("   2. Agregar permiso: pages_read_engagement")
        logger.error("   3. Generar nuevo token")
        logger.error("   4. Actualizar .env")
        return False

    if len(likes) == 0:
        logger.info("")
        logger.info("✅ Tu página no sigue a ninguna otra página")
        logger.info("   ¡Ya está limpia!")
        return True

    # Mostrar lista
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"📋 TU PÁGINA SIGUE A {len(likes)} PÁGINAS:")
    logger.info("=" * 70)

    for i, page in enumerate(likes, 1):
        category = page.get('category', 'Sin categoría')
        logger.info(f"{i:3d}. {page['name']:<40} ({category})")

    # Guardar lista en JSON para referencia
    output_file = Path(__file__).parent.parent.parent / "output" / "page_likes.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(likes, f, indent=2, ensure_ascii=False)

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"💾 Lista guardada en: {output_file}")
    logger.info("=" * 70)

    # Opciones
    logger.info("")
    logger.info("🎯 OPCIONES:")
    logger.info("")
    logger.info("1. Dejar de seguir TODAS las páginas")
    logger.info("2. Seleccionar páginas específicas para dejar de seguir")
    logger.info("3. Solo ver la lista (no hacer cambios)")
    logger.info("")

    try:
        choice = input("Elige una opción (1/2/3): ").strip()
    except EOFError:
        logger.info("\n📋 Lista mostrada. Usa el archivo JSON para ver los detalles.")
        logger.info("   Para remover páginas, ejecuta el script interactivamente.")
        return True

    if choice == '1':
        # Dejar de seguir todas
        logger.info("")
        logger.info("=" * 70)
        logger.info("⚠️  VAS A DEJAR DE SEGUIR TODAS LAS PÁGINAS")
        logger.info("=" * 70)

        try:
            confirm = input(f"¿Estás seguro? Escribe 'SI' para confirmar: ").strip()
        except EOFError:
            logger.info("❌ Operación cancelada")
            return False

        if confirm.upper() != 'SI':
            logger.info("❌ Operación cancelada")
            return False

        success_count = 0
        for i, page in enumerate(likes, 1):
            logger.info(f"🗑️  [{i}/{len(likes)}] Dejando de seguir: {page['name']}")
            if unlike_page(PAGE_ID, ACCESS_TOKEN, page['id']):
                success_count += 1
            else:
                logger.warning(f"   ⚠️  No se pudo procesar: {page['name']}")

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ LIMPIEZA COMPLETADA")
        logger.info("=" * 70)
        logger.info(f"✅ Se dejaron de seguir {success_count} de {len(likes)} páginas")

        return True

    elif choice == '2':
        # Selección específica
        logger.info("")
        logger.info("📝 Escribe los números de las páginas que quieres dejar de seguir")
        logger.info("   (separados por comas, ej: 1,3,5,7-10)")
        logger.info("")

        try:
            selection = input("Números: ").strip()
        except EOFError:
            logger.info("❌ Operación cancelada")
            return False

        if not selection:
            logger.info("❌ Operación cancelada")
            return False

        # Parsear selección
        selected_indices = set()
        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                # Rango
                start, end = part.split('-')
                selected_indices.update(range(int(start), int(end) + 1))
            else:
                # Número individual
                selected_indices.add(int(part))

        # Filtrar páginas seleccionadas
        selected_pages = [likes[i-1] for i in selected_indices if 1 <= i <= len(likes)]

        if len(selected_pages) == 0:
            logger.info("❌ No se seleccionó ninguna página válida")
            return False

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"VAS A DEJAR DE SEGUIR {len(selected_pages)} PÁGINAS:")
        logger.info("=" * 70)
        for page in selected_pages:
            logger.info(f"   - {page['name']}")

        logger.info("")
        try:
            confirm = input("¿Confirmas? (SI/no): ").strip()
        except EOFError:
            logger.info("❌ Operación cancelada")
            return False

        if confirm.upper() not in ['SI', 'SÍ', 'S', 'YES', 'Y']:
            logger.info("❌ Operación cancelada")
            return False

        success_count = 0
        for i, page in enumerate(selected_pages, 1):
            logger.info(f"🗑️  [{i}/{len(selected_pages)}] Dejando de seguir: {page['name']}")
            if unlike_page(PAGE_ID, ACCESS_TOKEN, page['id']):
                success_count += 1
            else:
                logger.warning(f"   ⚠️  No se pudo procesar: {page['name']}")

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ LIMPIEZA COMPLETADA")
        logger.info("=" * 70)
        logger.info(f"✅ Se dejaron de seguir {success_count} de {len(selected_pages)} páginas")

        return True

    else:
        # Solo ver
        logger.info("")
        logger.info("✅ Lista mostrada. No se hicieron cambios.")
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
