#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script inteligente para detectar boca basándose en:
1. Detectar cara blanca
2. Detectar ojos (óvalos negros)
3. Calcular posición de boca (entre ojos, un poco abajo)
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from collections import defaultdict

def find_white_face(arr):
    """Encuentra la región de la cara blanca"""
    height, width = arr.shape[:2]

    # Buscar píxeles blancos (cara)
    white_pixels = []
    for y in range(height):
        for x in range(width):
            r, g, b = arr[y, x]
            # Blanco o muy claro (cara)
            if r > 200 and g > 200 and b > 200:
                white_pixels.append((x, y))

    if not white_pixels:
        return None

    xs = [p[0] for p in white_pixels]
    ys = [p[1] for p in white_pixels]

    return {
        'min_x': min(xs),
        'max_x': max(xs),
        'min_y': min(ys),
        'max_y': max(ys),
        'center_x': sum(xs) // len(xs),
        'center_y': sum(ys) // len(ys)
    }

def find_eyes_in_face(arr, face_region):
    """Encuentra los ojos (óvalos negros) dentro de la cara"""

    # Buscar píxeles negros dentro de la región de la cara
    # (parte superior de la cara, donde están los ojos)
    eye_region_top = face_region['min_y']
    eye_region_bottom = face_region['min_y'] + int((face_region['max_y'] - face_region['min_y']) * 0.5)

    black_pixels = []
    for y in range(eye_region_top, eye_region_bottom):
        for x in range(face_region['min_x'], face_region['max_x']):
            if y < arr.shape[0] and x < arr.shape[1]:
                r, g, b = arr[y, x]
                # Negro (ojos)
                if r < 50 and g < 50 and b < 50:
                    black_pixels.append((x, y))

    if len(black_pixels) < 100:  # Muy pocos píxeles negros
        return None

    # Separar en 2 clusters (ojo izquierdo y derecho)
    # Agrupar por posición horizontal
    left_eye = []
    right_eye = []

    center_x = face_region['center_x']

    for x, y in black_pixels:
        if x < center_x:
            left_eye.append((x, y))
        else:
            right_eye.append((x, y))

    if not left_eye or not right_eye:
        return None

    # Calcular centro de cada ojo
    left_eye_center = (
        sum(p[0] for p in left_eye) // len(left_eye),
        sum(p[1] for p in left_eye) // len(left_eye)
    )

    right_eye_center = (
        sum(p[0] for p in right_eye) // len(right_eye),
        sum(p[1] for p in right_eye) // len(right_eye)
    )

    return {
        'left_eye': left_eye_center,
        'right_eye': right_eye_center,
        'center_x': (left_eye_center[0] + right_eye_center[0]) // 2,
        'center_y': (left_eye_center[1] + right_eye_center[1]) // 2,
        'distance': abs(right_eye_center[0] - left_eye_center[0])
    }

def calculate_mouth_position(face_region, eyes_data):
    """Calcula la posición de la boca basándose en ojos"""

    if not eyes_data:
        # Fallback: centro de la cara, 60% abajo
        mouth_x = face_region['center_x']
        mouth_y = face_region['min_y'] + int((face_region['max_y'] - face_region['min_y']) * 0.6)
        return mouth_x, mouth_y

    # Boca está:
    # - Horizontalmente: centrada entre los ojos
    # - Verticalmente: ~30% de la distancia entre ojos, abajo de los ojos

    mouth_x = eyes_data['center_x']

    # Distancia vertical desde ojos a boca (factor conservador 0.3)
    eye_to_mouth_distance = int(eyes_data['distance'] * 0.3)

    mouth_y = eyes_data['center_y'] + eye_to_mouth_distance

    return mouth_x, mouth_y

def detect_mouth(img_path):
    """Detecta la posición de la boca de forma inteligente"""

    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)

    height, width = arr.shape[:2]

    print(f"\nImagen: {img_path.name}")
    print(f"Tamano: {width}x{height}")

    # 1. Detectar cara blanca
    print("1. Detectando cara blanca...")
    face_region = find_white_face(arr)

    if not face_region:
        print("   ERROR: No se detectó cara blanca")
        return None

    print(f"   Cara detectada: x={face_region['min_x']}-{face_region['max_x']}, y={face_region['min_y']}-{face_region['max_y']}")

    # 2. Detectar ojos
    print("2. Detectando ojos...")
    eyes_data = find_eyes_in_face(arr, face_region)

    if eyes_data:
        print(f"   Ojo izquierdo: {eyes_data['left_eye']}")
        print(f"   Ojo derecho: {eyes_data['right_eye']}")
        print(f"   Distancia entre ojos: {eyes_data['distance']}px")
    else:
        print("   ADVERTENCIA: No se detectaron ojos claramente")

    # 3. Calcular posición de boca
    print("3. Calculando posicion de boca...")
    mouth_x, mouth_y = calculate_mouth_position(face_region, eyes_data)

    print(f"\nBOCA CALCULADA: ({mouth_x}, {mouth_y})")

    return mouth_x, mouth_y

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent.parent

    mama_path = base_dir / "assets" / "personajes_base" / "mama_base.png"
    papa_path = base_dir / "assets" / "personajes_base" / "papá_sumiso.png"

    print("=" * 70)
    print("DETECCION INTELIGENTE DE BOCA")
    print("=" * 70)

    mama_mouth = detect_mouth(mama_path)
    print("\n" + "-" * 70)
    papa_mouth = detect_mouth(papa_path)

    print("\n" + "=" * 70)
    print("CONFIGURACION SUGERIDA:")
    print("=" * 70)

    if mama_mouth:
        print(f"\n'mama': {{")
        print(f"    'center_x': {mama_mouth[0]},")
        print(f"    'center_y': {mama_mouth[1]},")
        print(f"}}")

    if papa_mouth:
        print(f"\n'papa': {{")
        print(f"    'center_x': {papa_mouth[0]},")
        print(f"    'center_y': {papa_mouth[1]},")
        print(f"}}")

    print("\n" + "=" * 70)
