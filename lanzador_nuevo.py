import subprocess
import webbrowser
import sys
import os
import time
import shutil
from multiprocessing import freeze_support

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def iniciar_app():
    os.environ["REFLEX_LAUNCHER_ACTIVE"] = "true"
    base_path = resource_path(".")
    os.chdir(base_path)
    
    # Clonamos el ejecutable para que Reflex encuentre un "python.exe"
    falso_python = os.path.join(base_path, "python.exe")
    if not os.path.exists(falso_python):
        try:
            shutil.copy(sys.executable, falso_python)
        except Exception: pass

    # Forzamos las rutas
    os.environ["PYTHONPATH"] = base_path
    os.environ["REFLEX_WEB_ROOT"] = os.path.join(base_path, ".web")
    os.environ["REFLEX_PYTHON_PATH"] = falso_python
    os.environ["PATH"] = base_path + os.pathsep + os.environ.get("PATH", "")

    print(f"--- CALCULADORA DE SALUD ---")
    
    # Buscamos el binario de reflex
    reflex_bin = resource_path("reflex.exe")
    
    # Usamos el falso_python para ejecutar reflex como módulo, es más estable
    comando = [falso_python, "-m", "reflex", "run", "--env", "prod", "--frontend-port", "3000"]

    try:
        process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy(),
            cwd=base_path
        )

        navegador_abierto = False
        for line in process.stdout:
            print(f"[MOTOR]: {line.strip()}")
            if "App running at" in line:
                if not navegador_abierto:
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