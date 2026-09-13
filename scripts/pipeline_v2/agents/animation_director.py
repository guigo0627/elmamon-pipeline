#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENTE 1: Director de Animación
Analiza transcripción y genera plan de animación con personajes explícitos e implícitos
"""

import sys
import os
from pathlib import Path
import json

# Fix encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from anthropic import Anthropic

SYSTEM_PROMPT = """Eres un Director de Animación experto especializado en videos tipo "Ignacio Animados" para Reels/Shorts.

Tu trabajo es analizar la transcripción de un audio y generar un plan detallado de animación.

## CAPACIDADES CRÍTICAS:

### 1. DETECCIÓN DE PERSONAJES IMPLÍCITOS
NO solo detectes quién habla - detecta quién DEBE estar en escena:
- Si alguien dice "te traté mal" → hay un "tú" presente (receptor)
- Si dice "mi esposo" → el esposo debe aparecer
- Si dice "mi hijo me preguntó" → el hijo debe estar presente

### 2. ANÁLISIS CONTEXTUAL
Identifica relaciones y roles:
- Relación entre personajes (esposos, madre-hijo, amigos, etc)
- Quién habla y quién escucha
- Emociones de AMBOS (no solo del que habla)

### 3. ASIGNACIÓN DE PERSONAJES
Basándote en contexto:
- Género (voz + contexto)
- Rol (esposo, esposa, hijo, amigo, etc)
- Estado emocional (feliz, triste, enojado, sumiso, etc)

### 4. PLANIFICACIÓN DE ESCENAS
Para cada segmento:
- Quién habla (animación de boca)
- Qué hace el otro personaje (reacción, gesto)
- Expresiones faciales de ambos
- Gestos corporales

## PERSONAJES DISPONIBLES:
- mujer / mama / esposa
- hombre / papa / esposo
- hijo_mayor / hijo
- hija
- amigo

## OUTPUT ESPERADO:
JSON con estructura:
{
  "analysis": {
    "speakers_talking": 1,
    "characters_in_scene": 2,
    "context": "descripción del contexto detectado",
    "relationship": "tipo de relación entre personajes"
  },
  "characters": [
    {
      "id": "character_1",
      "role": "esposa",
      "type": "mujer",
      "speaking": true,
      "emotions": ["disculpa", "emocional"],
      "position": "left"
    },
    {
      "id": "character_2",
      "role": "esposo",
      "type": "hombre",
      "speaking": false,
      "emotions": ["sumiso", "regañado"],
      "position": "right"
    }
  ],
  "scenes": [
    {
      "start": 0.0,
      "end": 5.0,
      "speaker_id": "character_1",
      "text": "Si alguna vez te traté mal...",
      "speaker_action": {
        "expression": "disculpa",
        "gesture": "hands_apologetic",
        "intensity": "medium"
      },
      "listener_action": {
        "expression": "sumiso",
        "gesture": "arms_crossed",
        "intensity": "low"
      },
      "camera": {
        "focus": "speaker",
        "zoom": 1.0
      }
    }
  ]
}

## IMPORTANTE:
- SIEMPRE busca personajes implícitos
- NO asumas que solo hay quien habla
- Analiza el CONTEXTO, no solo las palabras
- Piensa en cómo se vería visualmente

Responde SOLO con JSON válido, sin explicaciones adicionales.
"""


def analyze_transcription(transcription_data, api_key):
    """
    Analiza transcripción con Claude y genera plan de animación

    Args:
        transcription_data: Dict con transcripción de AssemblyAI
        api_key: API key de Anthropic

    Returns:
        dict: Plan de animación detallado
    """

    # Configurar cliente Anthropic (sin workspace - usar API directa)
    client = Anthropic(api_key=api_key)

    # Preparar contexto para Claude
    context = f"""
## TRANSCRIPCIÓN A ANALIZAR:

**Audio completo:** {transcription_data['text_full']}

**Duración:** {transcription_data['audio_duration']} segundos

**Speakers detectados hablando:** {len(transcription_data['speakers'])}

**Segmentos por speaker:**
"""

    for speaker in transcription_data['speakers']:
        context += f"\n### Speaker {speaker['speaker_id']}:\n"
        for seg in speaker['segments']:
            context += f"- [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}\n"

    context += """

## TU TAREA:

1. Analiza el contexto completo
2. Detecta personajes explícitos E IMPLÍCITOS
3. Identifica relaciones y emociones
4. Genera plan de animación detallado

Responde SOLO con el JSON del plan de animación.
"""

    # Llamar a Claude
    response = client.messages.create(
        model="claude-sonnet-4-5",  # Modelo actual del usuario
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": context
            }
        ]
    )

    # Extraer JSON de la respuesta
    response_text = response.content[0].text

    # Intentar parsear JSON
    try:
        # Limpiar markdown si existe
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]

        animation_plan = json.loads(response_text.strip())
        return animation_plan

    except json.JSONDecodeError as e:
        print(f"⚠️ Error parseando JSON: {e}")
        print(f"Respuesta cruda:\n{response_text}")
        return None


def main():
    """Test del agente"""
    print("🎬 Test AGENTE 1: Director de Animación\n")

    # Cargar transcripción de prueba
    base_dir = Path(__file__).parent.parent.parent.parent
    transcription_path = base_dir / "output" / "test_transcription" / "transcription.json"

    if not transcription_path.exists():
        print(f"❌ Transcripción no encontrada: {transcription_path}")
        return False

    with open(transcription_path, 'r', encoding='utf-8') as f:
        transcription_data = json.load(f)

    # API Key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY no configurada")
        return False

    print("📊 Analizando transcripción con AGENTE 1...")
    print(f"   Texto: {transcription_data['text_full'][:100]}...")
    print(f"   Speakers hablando: {len(transcription_data['speakers'])}")
    print()

    # Analizar
    animation_plan = analyze_transcription(transcription_data, api_key)

    if animation_plan:
        print("=" * 70)
        print("✅ PLAN DE ANIMACIÓN GENERADO")
        print("=" * 70)

        # Mostrar análisis
        if 'analysis' in animation_plan:
            analysis = animation_plan['analysis']
            print(f"\n📊 ANÁLISIS:")
            print(f"   Speakers hablando: {analysis.get('speakers_talking', 'N/A')}")
            print(f"   Personajes en escena: {analysis.get('characters_in_scene', 'N/A')}")
            print(f"   Contexto: {analysis.get('context', 'N/A')}")
            print(f"   Relación: {analysis.get('relationship', 'N/A')}")

        # Mostrar personajes
        if 'characters' in animation_plan:
            print(f"\n🎭 PERSONAJES ({len(animation_plan['characters'])}):")
            for char in animation_plan['characters']:
                speaking = "🗣️ HABLA" if char.get('speaking') else "👂 ESCUCHA"
                print(f"   {speaking} - {char['role'].upper()}")
                print(f"      Tipo: {char['type']}")
                print(f"      Emociones: {', '.join(char.get('emotions', []))}")
                print(f"      Posición: {char.get('position', 'N/A')}")
                print()

        # Mostrar escenas
        if 'scenes' in animation_plan:
            print(f"\n🎬 ESCENAS ({len(animation_plan['scenes'])}):")
            for i, scene in enumerate(animation_plan['scenes'][:3]):  # Primeras 3
                print(f"   Escena {i+1} [{scene['start']:.1f}s - {scene['end']:.1f}s]")
                print(f"      Texto: {scene['text'][:60]}...")
                if 'speaker_action' in scene:
                    print(f"      Hablante: {scene['speaker_action'].get('expression')} + {scene['speaker_action'].get('gesture')}")
                if 'listener_action' in scene:
                    print(f"      Oyente: {scene['listener_action'].get('expression')} + {scene['listener_action'].get('gesture')}")
                print()

        # Guardar
        output_path = base_dir / "output" / "test_transcription" / "animation_plan.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(animation_plan, f, ensure_ascii=False, indent=2)

        print(f"💾 Plan guardado: {output_path}")
        print("=" * 70)

        return True
    else:
        print("❌ No se pudo generar plan de animación")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
