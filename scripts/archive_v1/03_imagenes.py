#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa 3: Generación de imágenes para personajes, escenarios y cutaways
Usa Replicate API (Flux) con style_bible.json para generar imágenes en formato vertical 9:16
"""

import sys
import os
import json
import requests
import time
from pathlib import Path

# Configurar encoding UTF-8 en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar carpeta scripts al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    setup_logger,
    get_api_key,
    get_video_folder_by_session,
    load_style_bible
)

# Configurar logger
logger = setup_logger('imagenes')


def cargar_guion(session_id):
    """Carga el guion aprobado de un video"""
    video_folder = get_video_folder_by_session(session_id)
    if not video_folder:
        logger.error(f"❌ No se encontró carpeta para session_id: {session_id}")
        return None

    guion_path = os.path.join(video_folder, "guion.json")
    if not os.path.exists(guion_path):
        logger.error(f"❌ No se encontró guion en: {guion_path}")
        return None

    with open(guion_path, 'r', encoding='utf-8') as f:
        guion = json.load(f)

    logger.info(f"✅ Guion cargado: {guion_path}")
    return guion, video_folder


def analizar_imagenes_necesarias(guion, style_bible):
    """
    Analiza el guion y determina qué imágenes se necesitan generar.
    Retorna una lista de especificaciones de imágenes.
    """
    imagenes = []

    # 1. PERSONAJES - Analizar expresiones necesarias del diálogo
    personajes = guion.get('personajes', [])
    dialogo = guion.get('dialogo', [])

    # Mapear personajes a sus expresiones necesarias
    expresiones_por_personaje = {}

    for linea in dialogo:
        hablante = linea.get('hablante')
        texto = linea.get('linea', '')

        # Determinar expresión basada en el contenido y contexto
        if hablante not in expresiones_por_personaje:
            expresiones_por_personaje[hablante] = []

        # Detectar tipo de expresión necesaria
        if '¿' in texto:
            expresion = 'preguntando'
        elif 'Noooooo' in texto or 'güey' in texto or len(texto) > 100:
            expresion = 'dramatico_hablando'
        elif 'No mijo' in texto or 'No güey' in texto:
            expresion = 'confundida'
        elif 'Errrdaaaaa' in texto or '!' in texto:
            expresion = 'sorprendida'
        elif len(texto) < 20:
            expresion = 'normal'
        else:
            expresion = 'hablando'

        # Evitar duplicados
        if expresion not in expresiones_por_personaje[hablante]:
            expresiones_por_personaje[hablante].append(expresion)

    # Generar specs de imágenes para cada personaje y expresión
    for personaje in personajes:
        rol = personaje.get('rol')
        especie = personaje.get('especie') if rol == 'mascota' else None
        estado_animo = personaje.get('estado_animo', 'normal')

        # Obtener info del style_bible
        if rol == 'mascota' and especie:
            personaje_info = style_bible['mascotas'].get(especie, {})
            tipo_personaje = especie
        else:
            personaje_info = style_bible['humanos']['roles'].get(rol, {})
            tipo_personaje = rol

        # Determinar qué nombre usar para el personaje en el diálogo
        nombre_en_dialogo = especie if especie else rol

        # Generar imagen por cada expresión necesaria
        expresiones = expresiones_por_personaje.get(nombre_en_dialogo, ['normal'])

        for expresion in expresiones:
            imagenes.append({
                'tipo': 'personaje',
                'personaje': tipo_personaje,
                'rol': rol,
                'expresion': expresion,
                'estado_animo': estado_animo,
                'info': personaje_info,
                'filename': f"{tipo_personaje}_{expresion}.png"
            })

    # 2. CUTAWAYS - Buscar en el diálogo
    for linea in dialogo:
        if 'cutaway' in linea:
            cutaway = linea['cutaway']
            trigger = cutaway.get('trigger', 'cutaway')
            prompt_visual = cutaway.get('prompt_visual', '')

            imagenes.append({
                'tipo': 'cutaway',
                'trigger': trigger,
                'prompt_visual': prompt_visual,
                'filename': f"cutaway_{trigger.replace(' ', '_')}.png"
            })

    # 3. FONDO/ESCENARIO
    escenario = guion.get('escenario', 'sala')
    escenario_info = style_bible['escenarios'].get(escenario, {})

    imagenes.append({
        'tipo': 'fondo',
        'escenario': escenario,
        'info': escenario_info,
        'filename': f"fondo_{escenario}.png"
    })

    logger.info(f"📊 Análisis completado: {len(imagenes)} imágenes necesarias")
    logger.info(f"   - Personajes: {len([i for i in imagenes if i['tipo'] == 'personaje'])}")
    logger.info(f"   - Cutaways: {len([i for i in imagenes if i['tipo'] == 'cutaway'])}")
    logger.info(f"   - Fondos: {len([i for i in imagenes if i['tipo'] == 'fondo'])}")

    return imagenes


def generar_prompt_personaje(spec, style_bible):
    """Genera prompt optimizado para un personaje usando style_bible (estilo Paint IMPERFECTO)"""
    personaje = spec['personaje']
    expresion = spec['expresion']

    # Obtener info del style_bible
    if spec['rol'] == 'mascota':
        info = style_bible['mascotas'].get(personaje, {})
    else:
        info = style_bible['humanos']['roles'].get(personaje, {})

    # Mapear expresiones a poses/acciones
    expresiones_map = {
        'normal': 'standing neutral, arms at sides',
        'hablando': 'talking, one arm slightly raised',
        'dramatico_hablando': 'arms raised up dramatically',
        'preguntando': 'one arm pointing forward',
        'confundida': 'one hand on head',
        'sorprendida': 'both hands up surprised'
    }

    pose_desc = expresiones_map.get(expresion, 'standing neutral')

    # Construir prompt estilo dibujo simple con líneas gruesas
    if spec['rol'] == 'mascota':
        # MASCOTA = Hijo con cabeza forma de animal, piel blanca, ropa colorida
        especie = personaje

        # Obtener colores de ropa variables
        ropa_colores = info.get('ropa_colores_variables', ['blue t-shirt', 'gray pants'])
        import random
        camiseta = random.choice([r for r in ropa_colores if 'camiseta' in r or 't-shirt' in r])
        pantalones = random.choice([r for r in ropa_colores if 'pantalones' in r or 'pants' in r])

        if especie == 'gato':
            prompt = f"simple cartoon drawing, character with cat-shaped head with big triangular ears on top, large circular eyes, small nose dot, small mouth, WHITE skin on face and hands, human body wearing {camiseta} and {pantalones}, {pose_desc}, thick black outlines 3-4px width, flat colors, clean simple style, no shadows, no gradients, vertical format 9:16, white background"
        elif especie == 'perro':
            prompt = f"simple cartoon drawing, character with dog-shaped head with floppy ears, large circular eyes, small nose dot, small mouth, WHITE skin on face and hands, human body wearing {camiseta} and {pantalones}, {pose_desc}, thick black outlines 3-4px width, flat colors, clean simple style, vertical format 9:16, white background"
        else:
            prompt = f"simple cartoon drawing, character with {especie}-shaped head, large eyes, WHITE skin on face and hands, human body wearing {camiseta} and {pantalones}, {pose_desc}, thick black outlines 3-4px, flat colors, vertical 9:16, white background"
    else:
        # HUMANO = Cabeza blanca + cabello (si mujer) + piel blanca + ropa colorida
        rol = personaje

        # Obtener colores de ropa variables
        ropa_colores = info.get('ropa_colores_variables', ['yellow t-shirt', 'blue pants'])
        import random
        camiseta = random.choice([r for r in ropa_colores if 'camiseta' in r or 't-shirt' in r])
        pantalones = random.choice([r for r in ropa_colores if 'pantalones' in r or 'pants' in r])

        # Agregar cabello largo tupido para mujeres
        if rol in ['mamá', 'hija', 'abuela']:
            hair_desc = 'LONG thick BLACK hair falling down sides densely drawn'
        else:
            hair_desc = 'short dark hair or no hair'

        prompt = f"simple cartoon drawing, {rol} with WHITE circular head, large circular eyes, small nose, small mouth, {hair_desc}, WHITE skin on face and hands, human body wearing {camiseta} and {pantalones}, {pose_desc}, thick black outlines 3-4px width, flat colors, clean simple style, no shadows, vertical format 9:16, white background"

    return prompt


def generar_prompt_cutaway(spec, style_bible):
    """Genera prompt optimizado para un cutaway (FOTO REAL de animal EXPRESIVO)"""
    prompt_visual = spec['prompt_visual']

    # Cutaways = FOTOS REALES de animales con expresiones DRAMÁTICAS
    # Detectar animal
    if 'gato' in prompt_visual.lower():
        animal = 'cat'
    elif 'perro' in prompt_visual.lower():
        animal = 'dog'
    else:
        animal = 'cat'  # default

    # SIEMPRE expresión dramática/sorprendida para cutaways cómicos
    # Ignorar la expresión original del prompt_visual y usar expresión expresiva
    expression = 'very surprised shocked expression with WIDE OPEN EYES and OPEN MOUTH, dramatic facial expression'

    # Generar prompt para FOTO REAL EXPRESIVA
    prompt = f"realistic photograph of real {animal} with {expression}, natural pet photo taken at home, funny meme style, expressive face, clear focus on facial expression, vertical format 9:16, photographic style, high quality pet photo, dramatic expression"

    return prompt


def generar_prompt_fondo(spec, style_bible):
    """Genera prompt optimizado para un fondo/escenario (FOTO REAL)"""
    escenario = spec['escenario']
    info = spec['info']

    # Usar prompt de ejemplo del style_bible (ahora son prompts para fotos reales)
    if 'prompt_ejemplo' in info:
        prompt = info['prompt_ejemplo']
    else:
        # Fallback a foto real si no hay ejemplo
        descripcion = info.get('descripcion', '')
        prompt = f"realistic photograph of simple {escenario}, middle-class Latin American home, natural lighting, lived-in look, vertical format 9:16, real interior, photographic style, no characters"

    return prompt


def generar_imagen_replicate(prompt, negative_prompt, output_path, api_key):
    """
    Genera una imagen usando Replicate API (Flux)
    """
    logger.info(f"🎨 Generando imagen...")
    logger.info(f"   Prompt: {prompt[:100]}...")

    # Replicate API endpoint para Flux
    # Usando el modelo Flux Schnell (más rápido y económico)
    url = "https://api.replicate.com/v1/predictions"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    # Parámetros optimizados según style_bible
    # NOTA: Flux Schnell NO acepta negative_prompt ni guidance_scale
    data = {
        "version": "black-forest-labs/flux-schnell",
        "input": {
            "prompt": prompt,  # Solo positive prompt
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 90,
            "num_inference_steps": 4,  # Schnell funciona bien con 1-4 steps
            "go_fast": True  # Optimización adicional para Schnell
        }
    }

    try:
        # Crear predicción
        response = requests.post(url, headers=headers, json=data)

        # Si hay error, mostrar detalles completos
        if response.status_code != 201:
            logger.error(f"❌ Error {response.status_code}: {response.text}")
            return False

        response.raise_for_status()
        prediction = response.json()

        prediction_id = prediction['id']
        logger.info(f"⏳ Predicción creada: {prediction_id}")

        # Esperar a que complete
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            time.sleep(2)

            # Obtener estado
            status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()

            status = status_data['status']

            if status == 'succeeded':
                # Descargar imagen
                image_url = status_data['output'][0] if isinstance(status_data['output'], list) else status_data['output']
                logger.info(f"✅ Imagen generada: {image_url}")

                # Descargar y guardar
                img_response = requests.get(image_url)
                img_response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                logger.info(f"💾 Guardada en: {output_path}")
                return True

            elif status == 'failed':
                error = status_data.get('error', 'Unknown error')
                logger.error(f"❌ Generación falló: {error}")
                return False

            attempt += 1
            logger.info(f"⏳ Esperando... ({attempt}/{max_attempts}) Estado: {status}")

        logger.error(f"❌ Timeout esperando generación")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error en API: {e}")
        return False


def main(session_id):
    """Función principal"""
    logger.info("=" * 60)
    logger.info("🎨 INICIANDO GENERACIÓN DE IMÁGENES")
    logger.info("=" * 60)

    # 1. Cargar guion
    logger.info(f"📖 Cargando guion: {session_id}")
    resultado = cargar_guion(session_id)
    if not resultado:
        return False

    guion, video_folder = resultado
    logger.info(f"✅ Guion cargado desde: {video_folder}")

    # 2. Cargar style_bible
    logger.info("🎨 Cargando style_bible...")
    style_bible = load_style_bible()
    if not style_bible:
        logger.error("❌ No se pudo cargar style_bible.json")
        return False

    # 3. Analizar imágenes necesarias
    logger.info("🔍 Analizando imágenes necesarias...")
    imagenes_specs = analizar_imagenes_necesarias(guion, style_bible)

    logger.info(f"\n📋 PLAN DE GENERACIÓN:")
    for i, spec in enumerate(imagenes_specs, 1):
        logger.info(f"   {i}. {spec['tipo'].upper()}: {spec['filename']}")

    # Confirmar con usuario (opcional - comentar en producción)
    # input(f"\n⏸️  Presiona ENTER para generar {len(imagenes_specs)} imágenes...")

    # 4. Crear carpetas de salida
    personajes_folder = os.path.join(video_folder, "personajes")
    cutaways_folder = os.path.join(video_folder, "cutaways")
    fondo_folder = os.path.join(video_folder, "fondo")

    os.makedirs(personajes_folder, exist_ok=True)
    os.makedirs(cutaways_folder, exist_ok=True)
    os.makedirs(fondo_folder, exist_ok=True)

    # 5. Obtener API key
    api_key = get_api_key("replicate")
    if not api_key:
        logger.error("❌ No se encontró API key de Replicate")
        return False

    # 6. Generar negative prompt
    negative_prompt = style_bible['plantillas_prompts_flux']['negative_prompts']['SIEMPRE_INCLUIR']

    # 7. Generar cada imagen
    logger.info(f"\n🎨 GENERANDO {len(imagenes_specs)} IMÁGENES...")

    resultados = {
        'exitosas': 0,
        'fallidas': 0,
        'imagenes': []
    }

    for i, spec in enumerate(imagenes_specs, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"🖼️  IMAGEN {i}/{len(imagenes_specs)}: {spec['filename']}")
        logger.info(f"{'='*60}")

        # Generar prompt según tipo
        if spec['tipo'] == 'personaje':
            prompt = generar_prompt_personaje(spec, style_bible)
            output_folder = personajes_folder
        elif spec['tipo'] == 'cutaway':
            prompt = generar_prompt_cutaway(spec, style_bible)
            output_folder = cutaways_folder
        elif spec['tipo'] == 'fondo':
            prompt = generar_prompt_fondo(spec, style_bible)
            output_folder = fondo_folder

        output_path = os.path.join(output_folder, spec['filename'])

        # Generar imagen
        exito = generar_imagen_replicate(prompt, negative_prompt, output_path, api_key)

        if exito:
            resultados['exitosas'] += 1
            resultados['imagenes'].append({
                'filename': spec['filename'],
                'tipo': spec['tipo'],
                'path': output_path,
                'prompt': prompt,
                'status': 'success'
            })
            logger.info(f"✅ ÉXITO: {spec['filename']}")
        else:
            resultados['fallidas'] += 1
            resultados['imagenes'].append({
                'filename': spec['filename'],
                'tipo': spec['tipo'],
                'path': output_path,
                'prompt': prompt,
                'status': 'failed'
            })
            logger.error(f"❌ FALLO: {spec['filename']}")

        # Delay entre peticiones para evitar rate limiting (excepto última)
        if i < len(imagenes_specs):
            logger.info("⏳ Esperando 3 segundos antes de siguiente imagen...")
            time.sleep(3)

    # 8. Guardar reporte
    reporte_path = os.path.join(video_folder, "imagenes_reporte.json")
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump({
            'session_id': session_id,
            'total_imagenes': len(imagenes_specs),
            'exitosas': resultados['exitosas'],
            'fallidas': resultados['fallidas'],
            'imagenes': resultados['imagenes']
        }, f, indent=2, ensure_ascii=False)

    # 9. Resumen final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMEN DE GENERACIÓN")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Exitosas: {resultados['exitosas']}/{len(imagenes_specs)}")
    logger.info(f"❌ Fallidas: {resultados['fallidas']}/{len(imagenes_specs)}")
    logger.info(f"\n📁 CARPETAS DE SALIDA:")
    logger.info(f"   - Personajes: {personajes_folder}")
    logger.info(f"   - Cutaways: {cutaways_folder}")
    logger.info(f"   - Fondo: {fondo_folder}")
    logger.info(f"\n📄 Reporte guardado: {reporte_path}")
    logger.info(f"{'='*60}")

    return resultados['fallidas'] == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python 03_imagenes.py <session_id>")
        print("   Ejemplo: python 03_imagenes.py 20260904_230817")
        sys.exit(1)

    session_id = sys.argv[1]

    exito = main(session_id)
    sys.exit(0 if exito else 1)
