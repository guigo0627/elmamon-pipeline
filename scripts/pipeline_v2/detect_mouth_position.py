#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para detectar la posición de la boca en los personajes PNG
Encuentra píxeles negros (boca) en la región de la cara
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np

def find_mouth_region(img_path):
    """
    Detecta la región aproximada de la boca buscando píxeles negros
    en el área central de la cara
    """
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)

    height, width = arr.shape[:2]

    # Buscar en la región central (20-60% ancho, 20-50% alto)
    x_start = int(width * 0.20)
    x_end = int(width * 0.60)
    y_start = int(height * 0.20)
    y_end = int(height * 0.50)

    print(f"\nImagen: {img_path.name}")
    print(f"   Tamano: {width}x{height}")
    print(f"   Region de busqueda: x={x_start}-{x_end}, y={y_start}-{y_end}")

    # Buscar píxeles negros (boca)
    mouth_pixels = []

    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            r, g, b = arr[y, x]
            # Negro o muy oscuro (boca)
            if r < 50 and g < 50 and b < 50:
                mouth_pixels.append((x, y))

    if mouth_pixels:
        # Calcular centro de los píxeles negros
        xs = [p[0] for p in mouth_pixels]
        ys = [p[1] for p in mouth_pixels]

        center_x = sum(xs) // len(xs)
        center_y = sum(ys) // len(ys)

        min_y = min(ys)
        max_y = max(ys)

        print(f"\nBOCA DETECTADA:")
        print(f"   Centro: ({center_x}, {center_y})")
        print(f"   Rango Y: {min_y} - {max_y}")
        print(f"   Pixeles negros encontrados: {len(mouth_pixels)}")

        return center_x, center_y
    else:
        print("❌ No se detectó la boca")
        return None

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent.parent

    mama_path = base_dir / "assets" / "personajes_base" / "mama_base.png"
    papa_path = base_dir / "assets" / "personajes_base" / "papá_sumiso.png"

    print("=" * 70)
    print("DETECTANDO POSICION DE BOCA EN PERSONAJES")
    print("=" * 70)

    mama_mouth = find_mouth_region(mama_path)
    papa_mouth = find_mouth_region(papa_path)

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
