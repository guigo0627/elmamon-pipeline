#!/usr/bin/env python
"""
ORQUESTADOR PRINCIPAL - elmamon-pipeline

Ejecuta todas las etapas del pipeline de forma secuencial:
1. Generación de guion
2. Validación de guion
3. Generación de imágenes (próximamente)
4. Generación de audio (próximamente)
5. Animación (próximamente)
6. Montaje final (próximamente)
7. Subtítulos (próximamente)
8. Publicación (Fase 2+)
"""
import sys
import argparse
from pathlib import Path

# Agregar scripts/ al path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from utils import setup_logger, get_session_id, check_fase, PipelineError

# Importar las funciones de los módulos 01 y 02
import importlib.util
import os

def load_module_from_file(module_name, file_path):
    """Carga un módulo desde un archivo específico"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Cargar módulos de scripts
scripts_dir = Path(__file__).parent / "scripts"
mod_guion = load_module_from_file("mod_guion", scripts_dir / "01_guion.py")
mod_validador = load_module_from_file("mod_validador", scripts_dir / "02_validador.py")

generar_guion = mod_guion.generar_guion
validar_guion = mod_validador.validar_guion
reescribir_guion = mod_validador.reescribir_guion

logger = setup_logger("PIPELINE")

ETAPAS_DISPONIBLES = {
    1: "Generación de guion",
    2: "Validación de guion",
    3: "Generación de imágenes (próximamente)",
    4: "Generación de audio (próximamente)",
    5: "Animación (próximamente)",
    6: "Montaje final (próximamente)",
    7: "Subtítulos (próximamente)",
    8: "Publicación (Fase 2+)"
}

MAX_REINTENTOS_VALIDACION = 2

def ejecutar_pipeline(tema_opcional: str = None, solo_hasta_etapa: int = 2):
    """
    Ejecuta el pipeline completo o hasta una etapa específica

    Args:
        tema_opcional: Tema o situación para el guion (opcional)
        solo_hasta_etapa: Número de etapa hasta donde ejecutar (por defecto: 2)

    Returns:
        dict: Información de la corrida
    """
    session_id = get_session_id()

    logger.info("="*70)
    logger.info(f"🎬 INICIANDO PIPELINE - Sesión: {session_id}")
    logger.info(f"📍 Fase del proyecto: {check_fase()}")
    logger.info(f"🎯 Ejecutando hasta etapa: {solo_hasta_etapa}")
    logger.info("="*70)

    resultado = {
        "session_id": session_id,
        "etapas_completadas": [],
        "errores": []
    }

    try:
        # =====================================================
        # ETAPA 1: GENERACIÓN DE GUION
        # =====================================================
        if solo_hasta_etapa >= 1:
            logger.info(f"\n▶️  ETAPA 1: {ETAPAS_DISPONIBLES[1]}")
            logger.info("-" * 70)

            guion = generar_guion(session_id, tema_opcional)
            resultado["etapas_completadas"].append(1)
            resultado["guion"] = guion

            logger.info("✓ Etapa 1 completada\n")

        # =====================================================
        # ETAPA 2: VALIDACIÓN DE GUION
        # =====================================================
        if solo_hasta_etapa >= 2:
            logger.info(f"\n▶️  ETAPA 2: {ETAPAS_DISPONIBLES[2]}")
            logger.info("-" * 70)

            intento = 1
            guion_aprobado = False

            while intento <= MAX_REINTENTOS_VALIDACION + 1 and not guion_aprobado:
                aprobado, validacion = validar_guion(session_id, guion, intento)

                if aprobado:
                    guion_aprobado = True
                    resultado["etapas_completadas"].append(2)
                    resultado["validacion"] = validacion
                    logger.info("✓ Etapa 2 completada - Guion aprobado\n")
                else:
                    if intento > MAX_REINTENTOS_VALIDACION:
                        raise PipelineError(
                            f"Guion rechazado después de {MAX_REINTENTOS_VALIDACION} reintentos. "
                            "Genera un nuevo guion."
                        )

                    logger.warning(f"⚠️  Reescribiendo guion (intento {intento + 1}/{MAX_REINTENTOS_VALIDACION + 1})...")
                    guion = reescribir_guion(session_id, guion, validacion)
                    intento += 1

        # =====================================================
        # ETAPA 3-7: PRÓXIMAMENTE
        # =====================================================
        if solo_hasta_etapa >= 3:
            logger.warning(f"\n⏸️  ETAPAS 3-7: En desarrollo")
            logger.info("Las siguientes etapas estarán disponibles próximamente:")
            for etapa in range(3, 8):
                if etapa <= solo_hasta_etapa:
                    logger.info(f"   • Etapa {etapa}: {ETAPAS_DISPONIBLES[etapa]}")

        # =====================================================
        # RESUMEN FINAL
        # =====================================================
        logger.info("\n" + "="*70)
        logger.info("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        logger.info("="*70)
        logger.info(f"Sesión: {session_id}")
        logger.info(f"Etapas completadas: {', '.join(map(str, resultado['etapas_completadas']))}")
        logger.info(f"\nArchivos generados:")
        logger.info(f"  • Guion: assets_temp/guiones/{session_id}_guion_final.json")
        logger.info(f"  • Logs: logs/{session_id}.json")

        if solo_hasta_etapa == 2:
            logger.info(f"\n💡 Próximos pasos (cuando estén disponibles):")
            logger.info(f"   python pipeline.py --continuar {session_id} --hasta-etapa 7")

        logger.info("="*70 + "\n")

        return resultado

    except PipelineError as e:
        logger.error(f"\n❌ ERROR EN EL PIPELINE: {e}")
        resultado["errores"].append(str(e))
        raise

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrumpido por el usuario")
        raise

    except Exception as e:
        logger.error(f"\n❌ ERROR INESPERADO: {e}")
        resultado["errores"].append(str(e))
        raise

def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Pipeline automático para generar videos de comedia familiar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Generar guion y validarlo (Fase 1 actual)
  python pipeline.py

  # Con tema específico
  python pipeline.py --tema "El gato no quiere bañarse"

  # Ejecutar hasta una etapa específica
  python pipeline.py --hasta-etapa 2

  # Continuar una sesión anterior (próximamente)
  python pipeline.py --continuar 20260904_211456 --hasta-etapa 7
        """
    )

    parser.add_argument(
        "--tema",
        type=str,
        help="Tema o situación específica para el guion"
    )

    parser.add_argument(
        "--hasta-etapa",
        type=int,
        default=2,
        choices=range(1, 9),
        help="Ejecutar hasta esta etapa (por defecto: 2)"
    )

    parser.add_argument(
        "--continuar",
        type=str,
        metavar="SESSION_ID",
        help="Continuar una sesión anterior (próximamente)"
    )

    args = parser.parse_args()

    # Validación
    if args.continuar:
        logger.error("❌ La opción --continuar aún no está implementada")
        sys.exit(1)

    if args.hasta_etapa > 2:
        logger.warning(f"⚠️  Solo las etapas 1-2 están disponibles actualmente")
        logger.warning(f"   Se ejecutará hasta la etapa 2")
        args.hasta_etapa = 2

    try:
        ejecutar_pipeline(
            tema_opcional=args.tema,
            solo_hasta_etapa=args.hasta_etapa
        )
        sys.exit(0)

    except PipelineError as e:
        logger.error(f"Pipeline falló: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Pipeline interrumpido")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
