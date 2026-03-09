import subprocess
import webbrowser
import sys
import os
import time
import shutil
from multiprocessing import freeze_support

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def iniciar_app():
    # 1. Evitar bucles infinitos
    os.environ["REFLEX_LAUNCHER_ACTIVE"] = "true"
    
    base_path = resource_path(".")
    os.chdir(base_path)
    try:
        falso_python = os.path.join(base_path, "python.exe")
        if not os.path.exists(falso_python):
            shutil.copy(sys.executable, falso_python)
    except Exception:
        pass # Si falla por permisos, seguimos adelante
    
    # 2. Configuración de entorno para que Reflex no se pierda
    os.environ["PYTHONPATH"] = base_path
    os.environ["REFLEX_WEB_ROOT"] = os.path.join(base_path, ".web")
    
    # --- AJUSTES MAESTROS PARA EL BACKEND ---
    # A) Le decimos a Reflex que use el propio EXE como intérprete de Python
    os.environ["REFLEX_PYTHON_PATH"] = sys.executable
    
    # B) Forzamos modo producción para evitar que busque herramientas de desarrollo
    os.environ["REFLEX_ENV_MODE"] = "prod"
    
    # C) TRUCO DEL PATH: Añadimos la carpeta del EXE al PATH para que al buscar "python" se encuentre a sí mismo
    ruta_exe = os.path.dirname(sys.executable)
    os.environ["PATH"] = ruta_exe + os.pathsep + os.environ.get("PATH", "")
    # ----------------------------------------

    print(f"--- CALCULADORA DE SALUD ---")
    print(f"Iniciando desde: {base_path}")

    # Localizar el motor interno de Reflex
    posibles_reflex = [
        resource_path("reflex.exe"), 
        os.path.join(base_path, "scripts", "reflex.exe"),
        os.path.join(base_path, "bin", "reflex.exe")
    ]
    
    reflex_bin = None
    for ruta in posibles_reflex:
        if os.path.exists(ruta):
            reflex_bin = ruta
            break

    try:
        if reflex_bin:
            print(f"Usando motor interno: {reflex_bin}")
            comando = [reflex_bin, "run", "--env", "prod", "--frontend-port", "3000"]
        else:
            print("Aviso: Binario directo no hallado, intentando vía módulo...")
            comando = [sys.executable, "-m", "reflex", "run", "--env", "prod", "--frontend-port", "3000"]

        process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy(),
            cwd=base_path
        )

        print("Esperando logs del servidor (esto puede tardar)...")
        navegador_abierto = False
        
        for line in process.stdout:
            clean_line = line.strip()
            print(f"[MOTOR]: {clean_line}")
            
            # Detectar cuando el frontend está listo
            if "App running at" in clean_line or "http://localhost:3000" in clean_line:
                if not navegador_abierto:
                    print("\n¡SERVIDOR LISTO! Abriendo navegador...")
                    webbrowser.open("http://localhost:3000")
                    navegador_abierto = True

        process.wait()

    except Exception as e:
        print(f"\n[ERROR]: {e}")
    finally:
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    freeze_support()
    if os.environ.get("REFLEX_LAUNCHER_ACTIVE") == "true":
        pass
    else:
        iniciar_app()