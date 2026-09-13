#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 2: Análisis con AGENTE 1 (Director de Animación)
Input:  transcription.json
Output: animation_plan.json

NOTA: Este módulo debe ser ejecutado manualmente con Claude Code
      usando el Agent tool, ya que requiere acceso al modelo Claude.

Para ejecutar:
1. Abrir Claude Code
2. Usar comando: python scripts/pipeline_v2/02_analyze_request.py
3. El script generará un prompt para Claude Code
4. Copiar y ejecutar el prompt en Claude Code
"""

import sys
import os
import json
from pathlib import Path

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('analyze')


ANALYSIS_PROMPT_TEMPLATE = """
Eres un Director de Animación experto especializado en videos tipo "Ignacio Animados" para Reels/Shorts.

Analiza esta transcripción y genera un plan de animación detallado.

## TRANSCRIPCIÓN:

**Texto completo:** {text_full}
**Duración:** {duration} segundos
**Speakers hablando:** {num_speakers}

{segments}

## CAPACIDADES CRÍTICAS:

### 1. DETECCIÓN DE PERSONAJES IMPLÍCITOS
NO solo detectes quién habla - detecta quién DEBE estar en escena:
- Si alguien dice "te traté mal" → hay un "tú" presente (receptor)
- Si dice "mi esposo" → el esposo debe aparecer
- Analiza el CONTEXTO completo

### 2. EJEMPLO DEL AUDIO ACTUAL:
"Si alguna vez te traté mal, te insulté..."
→ Hay 2 personajes: quien habla (mujer) Y quien escucha (esposo regañado)

### 3. ANÁLISIS CONTEXTUAL:
- Identifica relaciones (esposos, madre-hijo, amigos)
- Emociones de AMBOS personajes
- Quién habla y quién reacciona

## PERSONAJES DISPONIBLES:
- mujer / mama / esposa
- hombre / papa / esposo
- hijo_mayor / hijo
- hija
- amigo

## GENERA JSON CON ESTA ESTRUCTURA:

{{
  "analysis": {{
    "speakers_talking": 1,
    "characters_in_scene": 2,
    "context": "mujer disculpándose con su esposo",
    "relationship": "esposos"
  }},
  "characters": [
    {{
      "id": "character_1",
      "role": "esposa",
      "type": "mujer",
      "speaking": true,
      "emotions": ["disculpa", "emocional"],
      "position": "left"
    }},
    {{
      "id": "character_2",
      "role": "esposo",
      "type": "hombre",
      "speaking": false,
      "emotions": ["sumiso", "regañado"],
      "position": "right"
    }}
  ],
  "scenes": [
    {{
      "start": 0.0,
      "end": 5.0,
      "speaker_id": "character_1",
      "text": "Si alguna vez te traté mal...",
      "speaker_action": {{
        "expression": "disculpa",
        "gesture": "hands_apologetic",
        "intensity": "medium"
      }},
      "listener_action": {{
        "expression": "sumiso",
        "gesture": "arms_crossed",
        "intensity": "low"
      }},
      "camera": {{
        "focus": "speaker",
        "zoom": 1.0
      }}
    }}
  ]
}}

Responde SOLO con el JSON, sin explicaciones adicionales.
"""


def generate_analysis_request(transcription_path, output_path):
    """
    Genera el prompt para Claude Code
    """
    logger.info("=" * 70)
    logger.info("📊 GENERANDO REQUEST PARA CLAUDE CODE")
    logger.info("=" * 70)

    # Leer transcripción
    with open(transcription_path, 'r', encoding='utf-8') as f:
        transcription = json.load(f)

    # Preparar segmentos
    segments_text = ""
    for speaker in transcription['speakers']:
        segments_text += f"\n**Speaker {speaker['speaker_id']}:**\n"
        for seg in speaker['segments']:
            segments_text += f"- [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}\n"

    # Generar prompt
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        text_full=transcription['text_full'],
        duration=transcription['audio_duration'],
        num_speakers=len(transcription['speakers']),
        segments=segments_text
    )

    # Guardar prompt
    prompt_file = output_path / "analysis_prompt.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

    logger.info(f"✅ Prompt generado: {prompt_file}")
    logger.info("")
    logger.info("📋 INSTRUCCIONES:")
    logger.info("")
    logger.info("1. Copia el contenido de: analysis_prompt.txt")
    logger.info("2. Pégalo en Claude Code")
    logger.info("3. Claude generará el animation_plan.json")
    logger.info("4. Guarda la respuesta en: animation_plan.json")
    logger.info("")
    logger.info("=" * 70)

    return prompt


def main():
    """Test del módulo"""
    base_dir = Path(__file__).parent.parent.parent
    transcription_path = base_dir / "output" / "test_transcription" / "transcription.json"
    output_path = base_dir / "output" / "test_transcription"

    if not transcription_path.exists():
        logger.error(f"❌ Transcripción no encontrada: {transcription_path}")
        return False

    prompt = generate_analysis_request(transcription_path, output_path)

    logger.info("\n📝 PREVIEW DEL PROMPT:\n")
    logger.info("-" * 70)
    logger.info(prompt[:500] + "\n...\n")
    logger.info("-" * 70)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
