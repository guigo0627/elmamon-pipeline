#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración central del Pipeline V2
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios base
BASE_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts" / "pipeline_v2"

# APIs
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')

# Configuración de video
VIDEO_CONFIG = {
    'width': 1080,
    'height': 1920,
    'fps': 30,
    'format': '9:16',  # Shorts/Reels
}

# Configuración de animación
ANIMATION_CONFIG = {
    'character_scale': 0.45,  # 45% de la altura del video
    'gestures_enabled': True,
    'lip_sync_precision': 'high',
}

# Configuración de edición
EDIT_CONFIG = {
    'cut_interval': 2.5,  # Segundos entre cortes
    'zoom_enabled': True,
    'memes_enabled': True,
    'subtitles_karaoke': True,
    'subtitle_position': 'bottom',
    'subtitle_font_size': 70,
}

# Configuración de transcripción
TRANSCRIPTION_CONFIG = {
    'language': 'es',  # Español
    'speaker_labels': True,  # Diarization
    'sentiment_analysis': False,  # No disponible en español
}

# Rhubarb
RHUBARB_PATH = BASE_DIR / "tools" / "rhubarb" / "Rhubarb-Lip-Sync-1.13.0-Windows" / "rhubarb.exe"

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
