"""
Utilidades compartidas para el pipeline elmamon
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import colorlog

# Cargar variables de entorno
load_dotenv()

# Configurar logging con colores
def setup_logger(name: str) -> logging.Logger:
    """Configura un logger con formato colorido"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s[%(name)s]%(reset)s %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger

# Directorios base
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
PROMPTS_DIR = DOCS_DIR / "prompts"
SPECS_DIR = DOCS_DIR / "specs"
ASSETS_TEMP_DIR = BASE_DIR / "assets_temp"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"

# Crear directorios si no existen
for dir_path in [ASSETS_TEMP_DIR, OUTPUT_DIR, LOGS_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

def get_session_id() -> str:
    """Genera un ID único para esta sesión/corrida"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_json(data: Dict[Any, Any], filepath: Path) -> None:
    """Guarda datos en formato JSON con indentación"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: Path) -> Dict[Any, Any]:
    """Carga datos desde un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_prompt(prompt_name: str) -> str:
    """Carga un prompt desde docs/prompts/"""
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_style_bible() -> Dict[str, Any]:
    """Carga la guía de estilo visual desde docs/specs/"""
    return load_json(SPECS_DIR / "style_bible.json")

def get_api_key(service: str) -> str:
    """Obtiene la API key de un servicio desde las variables de entorno"""
    key = os.getenv(f"{service.upper()}_API_KEY")
    if not key:
        raise ValueError(f"No se encontró la API key para {service}. Verifica tu archivo .env")
    return key

def log_to_file(session_id: str, stage: str, data: Dict[Any, Any]) -> None:
    """Registra información de una etapa en un archivo de log"""
    log_file = LOGS_DIR / f"{session_id}.json"

    # Cargar logs existentes o crear nuevo
    if log_file.exists():
        logs = load_json(log_file)
    else:
        logs = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "stages": {}
        }

    # Agregar log de esta etapa
    logs["stages"][stage] = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    # Guardar
    save_json(logs, log_file)

def check_fase() -> int:
    """Verifica en qué fase está el proyecto"""
    fase = int(os.getenv("FASE_ACTUAL", "1"))
    if fase not in [1, 2, 3]:
        raise ValueError(f"FASE_ACTUAL debe ser 1, 2 o 3. Valor actual: {fase}")
    return fase

def count_characters(text: str) -> int:
    """Cuenta caracteres en un texto (útil para límites de ElevenLabs)"""
    return len(text)

def estimate_duration(text: str, words_per_second: float = 2.5) -> float:
    """
    Estima la duración en segundos de un texto hablado.
    Promedio: 2.5 palabras por segundo en español conversacional.
    """
    words = len(text.split())
    return words / words_per_second

def get_next_video_number() -> int:
    """
    Obtiene el siguiente número de video disponible.
    Lee las carpetas en output/ y devuelve el siguiente número secuencial.

    Returns:
        int: Siguiente número de video (ej: 1, 2, 3, ...)
    """
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return 1

    # Buscar todas las carpetas que empiecen con número
    existing_folders = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]

    if not existing_folders:
        return 1

    # Extraer números de las carpetas (formato: 001-20260904)
    numbers = []
    for folder in existing_folders:
        folder_name = folder.name
        if '-' in folder_name:
            try:
                num = int(folder_name.split('-')[0])
                numbers.append(num)
            except ValueError:
                continue

    if not numbers:
        return 1

    return max(numbers) + 1

def create_video_output_folder(session_id: str) -> Path:
    """
    Crea una carpeta numerada para un video en output/.
    Formato: ###-yyyyMMdd

    Args:
        session_id: ID de la sesión (formato: yyyyMMdd_HHMMSS)

    Returns:
        Path: Ruta a la carpeta creada (ej: output/001-20260904/)
    """
    # Extraer fecha del session_id (primeros 8 caracteres: yyyyMMdd)
    date_str = session_id.split('_')[0]

    # Obtener siguiente número
    video_num = get_next_video_number()

    # Crear nombre de carpeta: ###-yyyyMMdd
    folder_name = f"{video_num:03d}-{date_str}"
    folder_path = OUTPUT_DIR / folder_name

    # Crear carpeta y subcarpetas
    folder_path.mkdir(parents=True, exist_ok=True)
    (folder_path / "personajes").mkdir(exist_ok=True)
    (folder_path / "audio").mkdir(exist_ok=True)
    (folder_path / "animaciones").mkdir(exist_ok=True)
    (folder_path / "cutaways").mkdir(exist_ok=True)

    return folder_path

def get_video_folder_by_session(session_id: str) -> Path:
    """
    Busca la carpeta de output correspondiente a un session_id.

    Args:
        session_id: ID de la sesión

    Returns:
        Path: Ruta a la carpeta del video, o None si no existe
    """
    date_str = session_id.split('_')[0]

    # Buscar carpeta que termine con la fecha
    for folder in OUTPUT_DIR.iterdir():
        if folder.is_dir() and folder.name.endswith(f"-{date_str}"):
            # Verificar si el guion.json tiene este session_id
            guion_path = folder / "guion.json"
            if guion_path.exists():
                try:
                    guion = load_json(guion_path)
                    if guion.get('session_id') == session_id:
                        return folder
                except:
                    continue

    return None

class PipelineError(Exception):
    """Excepción personalizada para errores del pipeline"""
    pass
