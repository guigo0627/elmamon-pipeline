# Backgrounds para Pipeline

Este directorio contiene las imágenes REALES de fondo para cada tipo de escenario.

## Estructura

```
backgrounds/
├── sala_casa/       # Salas de casas (medio/bajo estrato)
├── cocina/          # Cocinas sencillas
├── cuarto/          # Habitaciones/cuartos
├── gym/             # Gimnasios
├── supermercado/    # Supermercados
└── bano/            # Baños
```

## Requisitos de las imágenes

- **Formato:** JPG, JPEG o PNG
- **Resolución mínima:** 1920x1080 (Full HD)
- **Aspecto:** Preferiblemente 16:9 (se recortará a 9:16)
- **Contenido:** Fotografías REALES (no dibujos, no renders 3D)
- **Estilo:** Espacios de estrato socioeconómico medio/bajo
- **Iluminación:** Natural o realista

## Cómo agregar nuevos backgrounds

1. Descarga imágenes REALES del tipo de escenario
2. Guárdalas en el directorio correspondiente
3. Nombra los archivos descriptivamente:
   - `sala_01.jpg`, `sala_02.jpg`, etc.
   - `cocina_01.jpg`, `cocina_02.jpg`, etc.

## Escenarios soportados

| Escenario | Carpeta | Descripción |
|-----------|---------|-------------|
| Sala de casa | `sala_casa/` | Living rooms, salas de estar |
| Cocina | `cocina/` | Cocinas sencillas |
| Cuarto/Habitación | `cuarto/` | Dormitorios, cuartos |
| Gimnasio | `gym/` | Espacios de ejercicio |
| Supermercado | `supermercado/` | Pasillos, áreas de compras |
| Baño | `bano/` | Baños completos |

## Uso en el pipeline

El **AGENTE 1** (animation_director) analiza el audio y determina el escenario apropiado.

El **Módulo 04** (background_manager) selecciona aleatoriamente una imagen del directorio correspondiente.

```python
# Ejemplo: Para una conversación en sala de casa
# animation_plan.json contiene:
{
  "analysis": {
    "background_analysis": {
      "recommended_setting": "sala_casa"
    }
  }
}

# El pipeline busca en: assets/backgrounds/sala_casa/
# Selecciona aleatoriamente: sala_01.jpg, sala_02.jpg, etc.
```

## Estado actual

✅ `sala_casa/` - 1 imagen (sala_01.png)
⚠️ `cocina/` - Vacío (agregar imágenes)
⚠️ `cuarto/` - Vacío (agregar imágenes)
⚠️ `gym/` - Vacío (agregar imágenes)
⚠️ `supermercado/` - Vacío (agregar imágenes)
⚠️ `bano/` - Vacío (agregar imágenes)

## Fuentes recomendadas

- **Pexels**: https://www.pexels.com/ (gratis, sin atribución)
- **Unsplash**: https://unsplash.com/ (gratis, sin atribución)
- **Pixabay**: https://pixabay.com/ (gratis)

**Buscar términos:**
- "simple living room"
- "modest kitchen"
- "basic bedroom"
- "home gym"
- "supermarket aisle"
- "simple bathroom"

**Agregar:** "latin america", "simple", "modest" para estrato medio/bajo
