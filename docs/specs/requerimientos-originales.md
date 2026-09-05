# Proyecto: elmamon-pipeline

## Contexto y objetivo

Quiero que construyas conmigo un pipeline de automatización llamado **elmamon-pipeline**, cuyo objetivo es generar videos cortos (Reels de Facebook / YouTube Shorts) de **comedia familiar cotidiana**, de principio a fin, **sin intervención manual** (sin que yo tenga que subir imágenes, grabar audio, ni editar nada a mano).

El formato: una mascota antropomorfizada (perro, gato o loro) interactúa con 1 o 2 miembros de una familia humana en situaciones del día a día. La mecánica del chiste es la misma que validamos en el formato original: un personaje plantea algo con tono "serio" (una reflexión, un reclamo, un consejo) y otro corta con un remate absurdo o cotidiano que da el giro cómico. El plus de este formato es el reconocimiento familiar: el espectador debe verse reflejado en uno de los personajes o reconocer a alguien de su vida en ellos.

**Audiencia objetivo:** desde los 10-12 años en adelante, incluyendo adultos. Publicable sin restricciones en Facebook y YouTube.

**Criterio de éxito del contenido** (debe guiar la calidad del guion, no solo la técnica): el video debe generar risa tanto en un niño de 12 años como en un adulto de 35, y despertar reacciones de identificación como "así es mi papá/mamá", "eso me pasó a mí", "se lo voy a mandar a mis amigos". Si el guion no genera esa sensación, no debe pasar a producción (ver Validador de guion más abajo).

## Restricciones duras

- **Cero intervención manual**: nada de bancos de imágenes propios, nada de grabaciones mías, nada de mover archivos a mano. Todo el contenido visual y de audio se genera on-demand vía API en cada corrida.
- **Elenco variable, máximo 3 personajes**: siempre incluye a la mascota + 1 o 2 miembros de familia. La automatización decide la combinación según qué sirva mejor al chiste. Ejemplos de combinaciones válidas: mascota+papá+hijo, mascota+mamá+papá, mascota+dos hermanos, mascota+dueño, mascota+papá.
- **La mascota no tiene nombre propio.** Se refiere siempre por su rol/especie ("el perro", "la mascota"), nunca con un nombre — así cualquier espectador puede imaginar a su propia mascota en ese lugar.
- **Especies de mascota limitadas a 3 opciones fijas**: perro, gato o loro. La automatización elige cuál según el guion. No se generan otras especies.
- **Personalidad de la mascota**: base cómica/graciosa, pero con un "estado de ánimo" variable por guion (puede ser gruñón, cascarrabias, sarcástico, etc.) según lo que sirva mejor al remate. El diseño visual y la voz base de la mascota se mantienen fijos entre videos para dar identidad de canal; lo que cambia por guion es su actitud puntual.
- **Animación real, no swap de imágenes**: los personajes deben verse animados como si estuvieran actuando la conversación (movimiento de cabeza, gestos, lip-sync real sincronizado a su audio), no solo boca abierta/cerrada superpuesta.
- **Exageración facial obligatoria**: el diseño base de cada personaje (humano y mascota) debe estar dibujado con rasgos exagerados desde el origen — ojos grandes, cejas marcadas, boca expresiva — nunca un estilo realista o sobrio. Esto es un requisito de estilo, no opcional.
- **El audio debe dar risa por sí mismo**: no basta con que el guion sea gracioso, la voz elegida para cada personaje (timbre, entonación) debe ser inherentemente cómica/exagerada. Evitar voces neutras de narrador.
- **Lenguaje panlatino, no localismos de un solo país**: las expresiones cómicas usadas deben reconocerse ampliamente en Latinoamérica (México, Colombia, Panamá, etc.), evitando modismos que solo se entiendan en un país o que cambien de sentido entre países. Sin groserías fuertes, dado el rango de edad objetivo (10-12 años en adelante).
- **Composición profesional con cutaways**: el video no puede ser solo el plano fijo de los personajes hablando. Cuando el diálogo mencione algo visualizable, debe insertarse una imagen/clip adicional alusivo a eso, generado también por IA, manteniendo una identidad visual propia (nunca memes reales con derechos de autor).
- **Duración final**: máximo 30 segundos, formato vertical 1080x1920.
- **Ritmo de edición**: cambio de plano/corte cada 2-4 segundos para mantener retención, repartiendo el encuadre entre los personajes presentes en cada momento.
- **Sin dependencia de assets con copyright**: todo el arte (personajes, fondos, cutaways) se genera con modelos de imagen propios, nunca se usan memes o imágenes de terceros con derechos reservados.

## Arquitectura del pipeline

Orquestado íntegramente por Claude Code, en etapas secuenciales con checkpoints de calidad:

```
[1] Guion + selección de elenco + marcado de cutaways (Claude API)
      ↓
[1.5] Validador de guion, 4 criterios (segunda pasada de Claude API)
      ↓
[2] Diseño de personajes y fondo (API de imagen)
      ↓
[3] Generación de audio, 1 voz por personaje (ElevenLabs API)
      ↓
[4] Animación de personajes con lip-sync real (Hedra API)
      ↓
[5] Generación de cutaways (misma API de imagen + Ken Burns vía ffmpeg)
      ↓
[6] Montaje/composición final (ffmpeg)
      ↓
[7] Subtítulos estilo karaoke quemados (usando timestamps de ElevenLabs)
      ↓
[8] Publicación automática (n8n → Meta Graph API + YouTube Data API) — solo en fases 2 y 3
```

### Detalle por etapa

**1. Guion + elenco + cutaways (Claude API, modelo Sonnet)**

Salida en JSON estructurado, nunca texto libre:

```json
{
  "personajes": [
    {"rol": "mascota", "especie": "perro", "estado_animo": "sarcástico"},
    {"rol": "papá"},
    {"rol": "hijo"}
  ],
  "escenario": "sala de la casa",
  "dialogo": [
    {"hablante": "mascota", "linea": "..."},
    {"hablante": "papá", "linea": "..."},
    {"hablante": "hijo", "linea": "...", "cutaway": {"trigger": "palabra clave", "prompt_visual": "descripción de la imagen a generar"}}
  ],
  "duracion_estimada_seg": 28
}
```

Reglas para esta etapa:
- `especie` de la mascota: solo perro, gato o loro.
- `personajes`: entre 2 y 3 en total, la mascota siempre presente.
- El guion completo debe leerse en ≤28 segundos hablado (deja margen para intro/outro de 2s).
- Expresiones cómicas del diálogo: panlatinas, sin localismos de un solo país, sin groserías fuertes.

**1.5. Validador de guion (Claude API, segunda llamada)**

Evalúa el guion generado contra 4 criterios antes de dejarlo pasar a producción:

1. **Comedia universal** — ¿funciona igual de bien para un espectador de 12 años que para uno de 35?
2. **Gatillo de identificación** — ¿genera reacciones tipo "así es mi papá/mamá", "eso me pasó a mí", "se lo voy a mandar a mis amigos"?
3. **Lenguaje neutro panlatino** — ¿las expresiones usadas se entienden y funcionan en varios países, sin choques culturales ni groserías fuertes?
4. **Coherencia del personaje** — ¿el estado de ánimo asignado a la mascota en ese guion encaja con el remate?

Si el guion falla en cualquiera de los 4 puntos, se reescribe automáticamente antes de continuar — esto evita gastar en generación de imagen/audio/video con guiones flojos.

**2. Diseño visual (API de imagen — Flux Pro / Ideogram vía Replicate)**

- Un "style bible" fijo en el prompt: personajes humanos de línea simple/minimalista con rasgos exagerados (ojos grandes, cejas marcadas), y la mascota con un poco más de detalle/textura para que contraste visualmente en el plano — inspirado en el estilo de comedia gráfica cotidiana tipo webcomic/reel, sin copiar ningún diseño existente.
- Genera: imagen de cada personaje del elenco de ese video, imagen de fondo, e imágenes de cada cutaway marcado en el guion.
- El diseño de la mascota (por especie) y de cada rol familiar debe mantenerse consistente entre videos donde reaparezcan, para dar identidad de canal reconocible.
- Remoción de fondo de los personajes vía herramienta gratuita (rembg) para poder componerlos sobre el fondo.

**3. Audio (ElevenLabs API)**

- Una voz por personaje presente en el video (hasta 3), elegidas de la Voice Library priorizando timbres cómicos/exagerados — no voces neutras de narrador.
- Ajustar parámetros de ElevenLabs (`stability` bajo, `style` alto) para entonación más expresiva.
- Generación por línea (no un solo bloque), concatenando las líneas de cada personaje con silencios en los turnos de los demás.
- Obtener alignment/timestamps por palabra — se usa después para el lip-sync y para los subtítulos karaoke.

**4. Animación (Hedra API — modelo Character-3)**

- Cada personaje + su pista de audio combinada → clip de video con movimiento real de cabeza, gestos y boca sincronizados, con expresión facial exagerada acorde al diseño base.
- Resolución 720p como estándar (balance costo/calidad).

**5. Cutaways**

- Las imágenes generadas en el paso 2 se animan con Ken Burns (zoom/pan) vía ffmpeg — gratis, no requiere motor de video adicional.
- Se insertan en el timestamp exacto marcado por el guion, sincronizado con el alignment del audio.

**6. Montaje (ffmpeg orquestado por Claude Code)**

- Composición en capas: fondo + clips de personajes + cutaways posicionados en su timestamp.
- Con hasta 3 personajes en pantalla: encuadre cerrado en quien habla, los demás de fondo/perfil, repartiendo el plano vertical sin saturarlo.
- Corte de foco cada 2-4 segundos al personaje que habla.
- Exportación: vertical 1080x1920, ≤30s, H.264.

**7. Subtítulos**

- Karaoke-highlight por palabra usando el alignment de ElevenLabs.
- Estilo meme: tipografía sans-serif bold, alto contraste.

**8. Publicación (n8n)**

- Solo activo en fase 2 en adelante (ver roadmap).
- Sube automáticamente a Reels (Meta Graph API) y Shorts (YouTube Data API).
- Horario de publicación: jueves/viernes/sábado en fase 2 (3/semana); diario al escalar a fase 3.

## Herramientas y APIs

| Función | Herramienta | Tipo |
|---|---|---|
| Guion, selección de elenco, validador de calidad | Claude API (Sonnet) | Pago por uso |
| Imágenes (personajes, fondo, cutaways) | Flux Pro / Ideogram vía Replicate | Pago por uso |
| Remoción de fondo | rembg | Gratis (open source) |
| Voces (hasta 3 por video) | ElevenLabs API | Suscripción por créditos |
| Animación con lip-sync real | Hedra API (Character-3) | Suscripción por créditos |
| Animación ligera de cutaways | ffmpeg (Ken Burns) | Gratis |
| Montaje/composición final | ffmpeg | Gratis |
| Orquestación del pipeline | Claude Code | — |
| Publicación automática | n8n (autoalojado) + Meta Graph API + YouTube Data API | Gratis |

## Roadmap de adopción (3 fases)

**Fase 1 — Validación (planes gratuitos, sin publicar)**
Objetivo: confirmar que el resultado visual/narrativo cumple expectativas antes de invertir. Se generan videos de prueba, no se publican en redes.
- ElevenLabs Free, Hedra/Kling Free, Ideogram Free, Claude API pago mínimo.
- Capacidad aproximada: ~10 videos de prueba/mes, $0 de costo fijo.

**Fase 2 — Lanzamiento (planes básicos, empieza publicación automática)**
Se activa la publicación automática vía n8n. Meta: 3 videos/semana (~12/mes), aunque la capacidad real del plan básico de Hedra ronda 7 videos/mes — ajustar cadencia de publicación o complementar con créditos extra según resultados.
- Hedra Basic, ElevenLabs Starter, Claude API + imágenes pago por uso.

**Fase 3 — Escalado (licencias profesionales, buena aceptación en redes)**
Se sube a publicación diaria (~30 videos/mes).
- Hedra Professional, ElevenLabs Creator, Claude API + imágenes pago por uso a mayor volumen.

## Estructura de proyecto sugerida

Antes de crear cualquier archivo o carpeta en mi sistema, pídeme confirmación explícita (así lo hemos manejado en proyectos anteriores como drilococo-pipeline).

```
elmamon-pipeline/
├── config/              # style bible, prompts fijos, credenciales (.env)
├── scripts/
│   ├── 01_guion.py          # Claude API: guion + elenco + cutaways
│   ├── 02_validador.py      # Claude API: validador de guion (4 criterios)
│   ├── 03_imagenes.py       # Flux/Ideogram: personajes, fondo, cutaways
│   ├── 04_audio.py          # ElevenLabs: voces por personaje + alignment
│   ├── 05_animacion.py      # Hedra: lip-sync por personaje
│   ├── 06_montaje.py        # ffmpeg: composición final
│   └── 07_publicar.py       # n8n/APIs de publicación (fase 2+)
├── assets_temp/         # outputs intermedios de cada corrida (se limpia después)
├── output/              # video final listo para publicar
└── logs/                # registro de cada corrida para debugging
```

## Qué necesito que hagas primero

1. Propón la estructura de carpetas y el `.env` de configuración (sin crear nada aún, solo mostrarlo).
2. Escribe el prompt de sistema exacto para la etapa 1 (guion + elenco + cutaways), con el JSON de salida definido arriba.
3. Escribe el prompt de sistema exacto para la etapa 1.5 (validador de guion, 4 criterios).
4. Una vez validemos ambos prompts conmigo, seguimos con el resto de las etapas en orden.

Recuerda: cada vez que vayas a crear o modificar algo en mi sistema de archivos, pídeme confirmación antes de hacerlo.
