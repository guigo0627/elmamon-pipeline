"""
Etapa 1.5: Validador de guion
Evalúa el guion contra 4 criterios de calidad antes de pasar a producción
"""
import sys
import json
from pathlib import Path
from anthropic import Anthropic
from utils import (
    setup_logger, save_json, load_json, load_prompt,
    get_api_key, log_to_file, get_video_folder_by_session,
    ASSETS_TEMP_DIR, OUTPUT_DIR, PipelineError
)

logger = setup_logger("02_validador")

MAX_REINTENTOS = 2  # Número máximo de reescrituras automáticas

def validar_guion(session_id: str, guion: dict, intento: int = 1) -> tuple[bool, dict]:
    """
    Valida un guion contra los 4 criterios de calidad

    Args:
        session_id: ID único de esta sesión
        guion: Guion a validar
        intento: Número de intento (para tracking)

    Returns:
        tuple: (aprobado: bool, resultado_validacion: dict)
    """
    logger.info(f"Validando guion (intento {intento})...")

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

    # Cargar prompt de validador
    system_prompt = load_prompt("prompt_validador")

    # Construir mensaje con el guion a validar
    guion_texto = json.dumps(guion, ensure_ascii=False, indent=2)
    user_message = f"{guion_texto}"

    logger.info("Llamando a Claude API para validar guion...")

    try:
        # Llamada a Claude API (usando modelo más reciente)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extraer respuesta
        content = response.content[0].text.strip()

        # Intentar parsear JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        validacion = json.loads(content)

        # Validar estructura
        if "aprobado" not in validacion or "criterios" not in validacion:
            raise PipelineError("La respuesta del validador no tiene la estructura esperada")

        # Guardar resultado de validación en la carpeta del video
        video_folder = get_video_folder_by_session(session_id)
        if video_folder:
            validacion_path = video_folder / f"validacion_intento{intento}.json"
            save_json(validacion, validacion_path)

        # También guardar en assets_temp para compatibilidad
        validaciones_dir = ASSETS_TEMP_DIR / "guiones"
        validaciones_dir.mkdir(exist_ok=True)
        temp_validacion_path = validaciones_dir / f"{session_id}_validacion_intento{intento}.json"
        save_json(validacion, temp_validacion_path)

        # Mostrar resultados
        logger.info(f"\n{'='*60}")
        logger.info("RESULTADO DE VALIDACIÓN")
        logger.info(f"{'='*60}")

        for criterio, resultado in validacion["criterios"].items():
            status = "✓ PASA" if resultado["pasa"] else "✗ FALLA"
            logger.info(f"{status} - {criterio.replace('_', ' ').title()}")
            logger.info(f"   {resultado['razon']}")

        logger.info(f"\n{'='*60}")
        logger.info(f"DECISIÓN: {validacion['recomendacion']}")
        logger.info(f"{'='*60}\n")

        # Log para debugging
        log_to_file(session_id, f"02_validador_intento{intento}", {
            "status": "completed",
            "aprobado": validacion["aprobado"],
            "criterios": validacion["criterios"],
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        })

        return validacion["aprobado"], validacion

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON del validador: {e}")
        logger.error(f"Respuesta recibida: {content[:500]}")
        raise PipelineError(f"El validador no devolvió un JSON válido: {e}")

    except Exception as e:
        logger.error(f"Error al validar guion: {e}")
        log_to_file(session_id, f"02_validador_intento{intento}", {
            "status": "error",
            "error": str(e)
        })
        raise PipelineError(f"Error en validación de guion: {e}")

def reescribir_guion(session_id: str, guion_original: dict, feedback_validacion: dict) -> dict:
    """
    Reescribe el guion basándose en el feedback del validador

    Args:
        session_id: ID único de esta sesión
        guion_original: Guion que falló la validación
        feedback_validacion: Resultado de la validación con razones de fallo

    Returns:
        dict: Guion reescrito
    """
    logger.info("Reescribiendo guion basándose en feedback...")

    # Cargar cliente de Claude
    client = Anthropic(
        api_key=get_api_key("anthropic"),
        default_headers={
            "anthropic-workspace-id": "wrkspc_019itQXZVQDC6owakSmd5sah"
        }
    )

    # Cargar prompt original
    system_prompt = load_prompt("prompt_guion")

    # Construir mensaje con feedback
    problemas = []
    for criterio, resultado in feedback_validacion["criterios"].items():
        if not resultado["pasa"]:
            problemas.append(f"- {criterio.replace('_', ' ').title()}: {resultado['razon']}")

    problemas_texto = "\n".join(problemas)

    user_message = f"""El guion anterior falló la validación por los siguientes motivos:

{problemas_texto}

Guion original:
{json.dumps(guion_original, ensure_ascii=False, indent=2)}

Por favor, genera un NUEVO guion que corrija estos problemas específicos, manteniendo la estructura JSON requerida."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        content = response.content[0].text.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        guion_nuevo = json.loads(content)

        logger.info("✓ Guion reescrito exitosamente")

        return guion_nuevo

    except Exception as e:
        logger.error(f"Error al reescribir guion: {e}")
        raise PipelineError(f"Error en reescritura: {e}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python 02_validador.py <session_id>")
        sys.exit(1)

    session_id = sys.argv[1]

    # Cargar guion generado
    guion_path = ASSETS_TEMP_DIR / "guiones" / f"{session_id}_guion.json"
    if not guion_path.exists():
        logger.error(f"No se encontró el guion: {guion_path}")
        sys.exit(1)

    try:
        guion = load_json(guion_path)
        intento = 1

        while intento <= MAX_REINTENTOS + 1:
            # Validar guion
            aprobado, validacion = validar_guion(session_id, guion, intento)

            if aprobado:
                logger.info("✓ ¡GUION APROBADO! Listo para pasar a producción.")

                # Marcar como aprobado en la carpeta del video
                video_folder = get_video_folder_by_session(session_id)
                if video_folder:
                    aprobado_path = video_folder / "APROBADO.txt"
                    with open(aprobado_path, 'w') as f:
                        f.write(f"Guion aprobado en intento {intento}\n")
                        f.write(f"Fecha: {validacion['criterios']}\n")
                    print(f"\nVideo aprobado: {video_folder.name}")

                # También guardar en assets_temp para compatibilidad
                guion_final_path = ASSETS_TEMP_DIR / "guiones" / f"{session_id}_guion_final.json"
                save_json(guion, guion_final_path)

                print(f"\nProximo paso: python scripts/03_imagenes.py {session_id}")
                break

            else:
                if intento > MAX_REINTENTOS:
                    logger.error(f"❌ Guion rechazado después de {MAX_REINTENTOS} reintentos.")
                    logger.error("Considera generar un nuevo guion desde cero con: python scripts/01_guion.py")
                    sys.exit(1)

                logger.warning(f"Guion rechazado. Reescribiendo (intento {intento + 1}/{MAX_REINTENTOS + 1})...")
                guion = reescribir_guion(session_id, guion, validacion)

                # Guardar guion reescrito
                guion_path = ASSETS_TEMP_DIR / "guiones" / f"{session_id}_guion_intento{intento + 1}.json"
                save_json(guion, guion_path)

                intento += 1

    except PipelineError as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Proceso interrumpido por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()
