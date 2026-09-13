#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar personajes disponibles y sus variaciones
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def escanear_personajes(base_dir="assets/personajes_base"):
    """Escanea carpeta y lista personajes con sus variaciones"""

    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"❌ Carpeta no encontrada: {base_dir}")
        return {}

    personajes = defaultdict(list)

    # Escanear archivos
    for archivo in base_path.glob("*"):
        if archivo.suffix.lower() in ['.png', '.jpg', '.jpeg', '.jfif']:
            # Extraer personaje y expresión
            nombre = archivo.stem  # filename sin extensión

            if '_' in nombre:
                partes = nombre.rsplit('_', 1)  # Split desde la derecha, 1 vez
                personaje = partes[0]
                expresion = partes[1] if len(partes) > 1 else 'base'
            else:
                personaje = nombre
                expresion = 'base'

            personajes[personaje].append({
                'expresion': expresion,
                'archivo': archivo.name,
                'ruta': str(archivo)
            })

    return dict(personajes)


def mostrar_inventario():
    """Muestra inventario de personajes disponibles"""

    print("=" * 70)
    print("📋 INVENTARIO DE PERSONAJES DISPONIBLES")
    print("=" * 70)
    print()

    personajes = escanear_personajes()

    if not personajes:
        print("❌ No se encontraron personajes en assets/personajes_base/")
        return

    total_variaciones = 0

    for personaje in sorted(personajes.keys()):
        expresiones = personajes[personaje]
        total_variaciones += len(expresiones)

        print(f"🎭 {personaje.upper()}")
        print(f"   Variaciones ({len(expresiones)}):")

        for exp in sorted(expresiones, key=lambda x: x['expresion']):
            icono = "✅" if exp['expresion'] == 'base' else "  "
            print(f"   {icono} {exp['expresion']:20s} → {exp['archivo']}")

        print()

    print("=" * 70)
    print(f"📊 TOTAL: {len(personajes)} personajes, {total_variaciones} variaciones")
    print("=" * 70)

    return personajes


def get_personajes_disponibles():
    """Retorna lista simple de personajes para uso en otros scripts"""
    personajes = escanear_personajes()
    return list(personajes.keys())


def get_expresiones_personaje(personaje):
    """Retorna expresiones disponibles para un personaje específico"""
    personajes = escanear_personajes()
    if personaje in personajes:
        return [exp['expresion'] for exp in personajes[personaje]]
    return []


def validar_personaje_expresion(personaje, expresion):
    """Verifica si existe una combinación personaje + expresión"""
    personajes = escanear_personajes()
    if personaje not in personajes:
        return False, f"Personaje '{personaje}' no encontrado"

    expresiones_disponibles = [exp['expresion'] for exp in personajes[personaje]]
    if expresion not in expresiones_disponibles:
        return False, f"Expresión '{expresion}' no disponible para '{personaje}'. Disponibles: {expresiones_disponibles}"

    return True, "OK"


if __name__ == '__main__':
    mostrar_inventario()
