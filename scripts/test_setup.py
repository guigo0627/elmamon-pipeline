"""
Script de verificación de configuración inicial
Verifica que todo esté listo para empezar a generar videos
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cargar .env
load_dotenv()

def check_mark(condition):
    """Retorna un check mark o una X según la condición"""
    return "✅" if condition else "❌"

def test_api_keys():
    """Verifica que las API keys necesarias estén configuradas"""
    print("\n" + "="*60)
    print("1️⃣  VERIFICANDO API KEYS")
    print("="*60)

    required_keys = {
        "ANTHROPIC_API_KEY": "Claude API",
        "REPLICATE_API_TOKEN": "Replicate (Flux/Ideogram)",
        "ELEVENLABS_API_KEY": "ElevenLabs",
        "HEDRA_API_KEY": "Hedra"
    }

    all_ok = True
    for key, name in required_keys.items():
        value = os.getenv(key)
        is_set = value is not None and value != "" and value != "tu_clave_aqui" and value != "tu_token_aqui"
        print(f"{check_mark(is_set)} {name}: {'Configurada' if is_set else 'NO CONFIGURADA'}")
        if not is_set:
            all_ok = False
            print(f"   → Edita .env y agrega: {key}=...")

    return all_ok

def test_ffmpeg():
    """Verifica que ffmpeg esté instalado"""
    print("\n" + "="*60)
    print("2️⃣  VERIFICANDO FFMPEG")
    print("="*60)

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ ffmpeg instalado: {version_line}")
            return True
        else:
            print("❌ ffmpeg no responde correctamente")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg NO está instalado o no está en PATH")
        print("   → Windows: winget install ffmpeg")
        print("   → Linux: sudo apt install ffmpeg")
        print("   → Mac: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error al verificar ffmpeg: {e}")
        return False

def test_directories():
    """Verifica que las carpetas necesarias existan"""
    print("\n" + "="*60)
    print("3️⃣  VERIFICANDO ESTRUCTURA DE CARPETAS")
    print("="*60)

    base_dir = Path(__file__).resolve().parent.parent
    required_dirs = [
        "config",
        "scripts",
        "assets_temp",
        "output",
        "logs"
    ]

    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        exists = dir_path.exists()
        print(f"{check_mark(exists)} {dir_name}/")
        if not exists:
            all_ok = False
            print(f"   → Crear con: mkdir {dir_name}")

    return all_ok

def test_dependencies():
    """Verifica que las dependencias Python estén instaladas"""
    print("\n" + "="*60)
    print("4️⃣  VERIFICANDO DEPENDENCIAS PYTHON")
    print("="*60)

    required_packages = [
        "anthropic",
        "requests",
        "replicate",
        "elevenlabs",
        "dotenv",
        "PIL",
        "colorlog"
    ]

    all_ok = True
    for package in required_packages:
        # Mapear nombres de paquetes a nombres de importación
        import_name = package
        if package == "dotenv":
            import_name = "dotenv"
        elif package == "PIL":
            import_name = "PIL"

        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} NO instalado")
            all_ok = False

    if not all_ok:
        print("\n   → Instalar con: pip install -r requirements.txt")

    return all_ok

def test_config_files():
    """Verifica que los archivos de configuración existan"""
    print("\n" + "="*60)
    print("5️⃣  VERIFICANDO ARCHIVOS DE CONFIGURACIÓN")
    print("="*60)

    base_dir = Path(__file__).resolve().parent.parent
    config_files = [
        ("docs/specs/style_bible.json", "Guía de estilo visual"),
        ("docs/prompts/prompt_guion.txt", "Prompt de guion"),
        ("docs/prompts/prompt_validador.txt", "Prompt de validador"),
        (".env", "Credenciales (copiar de .env.template)")
    ]

    all_ok = True
    for file_path, description in config_files:
        full_path = base_dir / file_path
        exists = full_path.exists()
        print(f"{check_mark(exists)} {file_path}: {description}")
        if not exists:
            all_ok = False
            if file_path == ".env":
                print(f"   → Crear con: cp .env.template .env")

    return all_ok

def main():
    """Función principal"""
    print("\n" + "🔍 "*20)
    print("VERIFICACIÓN DE CONFIGURACIÓN - elmamon-pipeline")
    print("🔍 "*20)

    results = {
        "API Keys": test_api_keys(),
        "ffmpeg": test_ffmpeg(),
        "Directorios": test_directories(),
        "Dependencias": test_dependencies(),
        "Config Files": test_config_files()
    }

    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)

    all_passed = all(results.values())

    for check_name, passed in results.items():
        print(f"{check_mark(passed)} {check_name}")

    print("\n" + "="*60)

    if all_passed:
        print("✅ ¡TODO LISTO! Puedes empezar a generar videos.")
        print("\nPróximo paso:")
        print("  python scripts/01_guion.py")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ Hay problemas de configuración. Revisa los errores arriba.")
        print("\nVerifica:")
        print("  1. Que .env esté configurado con tus API keys")
        print("  2. Que ffmpeg esté instalado")
        print("  3. Que hayas ejecutado: pip install -r requirements.txt")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
