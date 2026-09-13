"""
Etapa 1: Generación de guion + elenco + cutaways
Usa Claude API (Sonnet) para generar el guion estructurado
"""
import sys
import json
from pathlib import Path
from anthropic import Anthropic
from utils import (
    setup_logger, get_session_id, save_json, load_prompt,
    get_api_key, log_to_file, create_video_output_folder,
    ASSETS_TEMP_DIR, PipelineError
)

logger = setup_logger("01_guion")

def generar_guion(session_id: str, tema_opcional: str = None) -> dict:
    """
    Genera un guion completo usando Claude API

    Args:
        session_id: ID único de esta sesión
        tema_opcional: Tema o situación específica (opcional)

    Returns:
        dict: Guion estructurado con personajes, diálogo, cutaways
    """
    logger.info(f"Iniciando generación de guion para sesión {session_id}")

    # Cargar cliente de Claude
    try:
        client = Anthropic(
            api_key=get_api_key("anthropic"),
            default_headers={
                "anthropic-workspace-id": "wrkspc_019itQXZVQDC6owakSmd5sah"
            }
        )
    except ValueError as e:
        raise PipelineError(f"Error al cargar API key de Claude: {e}")

    # Cargar prompt de sistema
    system_prompt = load_prompt("prompt_guion")

    # Construir mensaje de usuario
    user_message = "Genera un guion original siguiendo todas las reglas especificadas."
    if tema_opcional:
        user_message = f"Genera un guion original sobre el siguiente tema o situación: {tema_opcional}\n\nSigue todas las reglas especificadas en el sistema."

    logger.info("Llamando a Claude API para generar guion...")

    try:
        # Llamada a Claude API (usando modelo más reciente)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extraer respuesta
        content = response.content[0].text.strip()

        # Intentar parsear JSON (Claude puede incluir ```json``` en la respuesta)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        guion = json.loads(content)

        # Validar estructura básica
        if not all(k in guion for k in ["personajes", "escenario", "dialogo"]):
            raise PipelineError("El guion generado no tiene la estructura esperada")

        # Agregar session_id al guion
        guion["session_id"] = session_id

        # Crear carpeta de output numerada para este video
        video_folder = create_video_output_folder(session_id)

        # Guardar guion en la carpeta del video
        guion_path = video_folder / "guion.json"
        save_json(guion, guion_path)

        # También guardar en assets_temp para compatibilidad temporal
        guiones_dir = ASSETS_TEMP_DIR / "guiones"
        guiones_dir.mkdir(exist_ok=True)
        temp_guion_path = guiones_dir / f"{session_id}_guion.json"
        save_json(guion, temp_guion_path)

        logger.info(f"✓ Guion generado exitosamente")
        logger.info(f"  - Carpeta: {video_folder.name}")
        logger.info(f"  - Personajes: {len(guion['personajes'])}")
        logger.info(f"  - Líneas de diálogo: {len(guion['dialogo'])}")
        logger.info(f"  - Escenario: {guion['escenario']}")
        logger.info(f"  - Duración estimada: {guion.get('duracion_estimada_seg', 'N/A')} seg")

        # Log para debugging
        log_to_file(session_id, "01_guion", {
            "status": "success",
            "video_folder": str(video_folder),
            "guion_path": str(guion_path),
            "personajes": guion["personajes"],
            "num_lineas": len(guion["dialogo"]),
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        })

        return guion

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON de Claude: {e}")
        logger.error(f"Respuesta recibida: {content[:500]}")
        raise PipelineError(f"Claude no devolvió un JSON válido: {e}")

    except Exception as e:
        logger.error(f"Error al generar guion: {e}")
        log_to_file(session_id, "01_guion", {
            "status": "error",
            "error": str(e)
        })
        raise PipelineError(f"Error en generación de guion: {e}")

def main():
    """Función principal"""
    # Obtener tema opcional de argumentos
    tema = sys.argv[1] if len(sys.argv) > 1 else None

    # Generar ID de sesión
    session_id = get_session_id()

    try:
        # Generar guion
        guion = generar_guion(session_id, tema)

        print("\n" + "="*50)
        print("GUION GENERADO EXITOSAMENTE")
        print("="*50)
        print(f"\nSesión: {session_id}")
        print(f"Personajes: {', '.join([p['rol'] for p in guion['personajes']])}")
        print(f"Escenario: {guion['escenario']}")
        print(f"\nDiálogo:")
        for i, linea in enumerate(guion['dialogo'], 1):
            print(f"  {i}. {linea['hablante']}: {linea['linea']}")
            if 'cutaway' in linea:
                print(f"     [CUTAWAY: {linea['cutaway']['trigger']}]")

        print(f"\nGuardado en: output/{video_folder.name}/guion.json")
        print(f"\nProximo paso: python scripts/02_validador.py {session_id}")

    except PipelineError as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Proceso interrumpido por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()
