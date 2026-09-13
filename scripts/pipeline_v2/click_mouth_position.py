#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script interactivo para marcar la posición de la boca
El usuario hace clic donde debe estar la boca y se guardan las coordenadas
"""

import sys
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Coordenadas seleccionadas
mouth_positions = {}
current_character = None

def onclick(event):
    """Captura el clic del usuario"""
    global mouth_positions, current_character

    if event.xdata is not None and event.ydata is not None:
        x = int(event.xdata)
        y = int(event.ydata)

        mouth_positions[current_character] = (x, y)

        print(f"\n✓ {current_character}: Boca marcada en ({x}, {y})")
        print("  Cierra esta ventana para continuar...")

        # Dibujar un círculo en la posición seleccionada
        ax = event.inaxes
        circle = patches.Circle((x, y), 30, linewidth=3, edgecolor='red', facecolor='none')
        ax.add_patch(circle)

        # Dibujar una cruz
        ax.plot([x-20, x+20], [y, y], 'r-', linewidth=2)
        ax.plot([x, x], [y-20, y+20], 'r-', linewidth=2)

        plt.draw()

def select_mouth_position(character_name, image_path):
    """Muestra la imagen y permite hacer clic"""
    global current_character
    current_character = character_name

    img = Image.open(image_path)

    fig, ax = plt.subplots(figsize=(10, 14))
    ax.imshow(img)
    ax.set_title(f'{character_name.upper()}: HAZ CLIC DONDE DEBE ESTAR LA BOCA',
                 fontsize=16, fontweight='bold', pad=20)
    ax.axis('on')

    # Conectar evento de clic
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.tight_layout()
    plt.show()

    return mouth_positions.get(character_name)

def main():
    """Script principal"""
    base_dir = Path(__file__).parent.parent.parent

    mama_path = base_dir / "assets" / "personajes_base" / "mama_base.png"
    papa_path = base_dir / "assets" / "personajes_base" / "papá_sumiso.png"

    print("=" * 70)
    print("SELECTOR INTERACTIVO DE POSICION DE BOCA")
    print("=" * 70)
    print("\nINSTRUCCIONES:")
    print("1. Se abrirá una ventana con la imagen del personaje")
    print("2. HAZ CLIC en el centro de donde DEBE estar la boca")
    print("3. Verás un círculo rojo marcando tu selección")
    print("4. Cierra la ventana para continuar con el siguiente personaje")
    print("\nPresiona ENTER para comenzar...")
    input()

    # Seleccionar boca de mamá
    print("\n" + "=" * 70)
    print("PASO 1: MAMA")
    print("=" * 70)
    mama_mouth = select_mouth_position('mama', mama_path)

    if not mama_mouth:
        print("ERROR: No seleccionaste la boca de mamá")
        return False

    # Seleccionar boca de papá
    print("\n" + "=" * 70)
    print("PASO 2: PAPA")
    print("=" * 70)
    papa_mouth = select_mouth_position('papa', papa_path)

    if not papa_mouth:
        print("ERROR: No seleccionaste la boca de papá")
        return False

    # Mostrar resultados
    print("\n" + "=" * 70)
    print("COORDENADAS SELECCIONADAS:")
    print("=" * 70)
    print(f"\nMamá: {mama_mouth}")
    print(f"Papá: {papa_mouth}")

    # Generar configuración
    print("\n" + "=" * 70)
    print("CONFIGURACION PARA COPIAR:")
    print("=" * 70)
    print(f"""
'mama': {{
    'center_x': {mama_mouth[0]},
    'center_y': {mama_mouth[1]},
}},
'papa': {{
    'center_x': {papa_mouth[0]},
    'center_y': {papa_mouth[1]},
}}
""")

    # Preguntar si actualizar automáticamente
    print("\n¿Actualizar automáticamente el archivo 03_png_character_animator.py? (s/n): ", end='')
    respuesta = input().strip().lower()

    if respuesta == 's':
        # Actualizar archivo
        animator_path = Path(__file__).parent / "03_png_character_animator.py"

        with open(animator_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar y reemplazar las coordenadas
        import re

        # Reemplazar mamá
        content = re.sub(
            r"'mama':\s*\{[^}]*'center_x':\s*\d+,.*?'center_y':\s*\d+,",
            f"'mama': {{\n        'center_x': {mama_mouth[0]},  # CLIC MANUAL\n        'center_y': {mama_mouth[1]},  # CLIC MANUAL",
            content,
            flags=re.DOTALL
        )

        # Reemplazar papá
        content = re.sub(
            r"'papa':\s*\{[^}]*'center_x':\s*\d+,.*?'center_y':\s*\d+,",
            f"'papa': {{\n        'center_x': {papa_mouth[0]},  # CLIC MANUAL\n        'center_y': {papa_mouth[1]},  # CLIC MANUAL",
            content,
            flags=re.DOTALL
        )

        with open(animator_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✓ Archivo actualizado: {animator_path}")
        print("\nAhora ejecuta: python 03_png_character_animator.py")
        print("para generar los tests con las coordenadas correctas.")

    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelado por el usuario")
        sys.exit(1)
