import subprocess
import webbrowser
import sys
import os
import time
from multiprocessing import freeze_support

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def iniciar_app():
    # Configuramos la ruta de la web
    os.environ["REFLEX_WEB_ROOT"] = resource_path(".web")
    
    try:
        print("Iniciando servidor de Salud... No cierres esta ventana.")
        
        # Usamos sys.executable -m reflex para mayor seguridad
        comando = [sys.executable, "-m", "reflex", "run", "--env", "prod"]
        
        # Popen con creación de grupo de procesos para evitar que se cierren juntos
        process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy() # Pasamos las variables de entorno actuales
        )

        print("Esperando a que el servidor esté listo...")
        time.sleep(30) 
        
        webbrowser.open("http://localhost:3000")

        # Esto mantiene la consola viva y muestra los logs de Reflex
        for line in process.stdout:
            print(f"[Reflex]: {line}", end="")

    except Exception as e:
        print(f"\n¡UPS! Error crítico: {e}")
        input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    # ESTO ES LO MÁS IMPORTANTE
    freeze_support()
    
    # Comprobamos que no se esté intentando ejecutar un subproceso interno de Reflex
    # Si detecta que ya hay un proceso hijo, no vuelve a ejecutar iniciar_app()
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        pass 
    else:
        iniciar_app()