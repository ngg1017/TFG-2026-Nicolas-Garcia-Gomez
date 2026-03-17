import reflex as rx
import os
import tempfile
import time
import asyncio
import glob


class State(rx.State):
    rutas_archivos: list[str]
    nombres_archivos: list[str]
    nombres_archivos_eliminados: list[str]
    cargados: int
    barra: bool = False

    async def handle_upload(self, files: list[rx.UploadFile]):

        self.cargados = 0
        self.nombres_archivos_eliminados = []

        #Conseguimos avisar para activar la barra de carga
        self.barra = True
        yield

        #Controlar que el maximo de archivos es 3
        if len(files) > 3:
            self.barra = False
            yield rx.window_alert("El maximo de archivos para subir a la vez son 3 csv") 
            return

        #Controla que los archivos solo sean de tipo csv
        for file in files:
            if file.name.split(".")[1] != "csv":
                self.barra = False 
                yield rx.window_alert("El tipo de archivo a subir es CSV") 
                return

        for file in files:  
            try: 
                #Creamos un archivo temporal fisico en el disco
                #delete=False es vital para que el archivo no se borre al cerrar el 'with'
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                    contenido = await file.read()
                    tmp.write(contenido)

                    #Impide que se guarden mas de 3 y los borra fisicamente
                    while len(self.rutas_archivos) >= 3:
                        #Extraemos las referencias del archivo mas antiguo
                        ruta_a_borrar = self.rutas_archivos[0]
                        nombre_a_borrar = self.nombres_archivos[0]

                        #Borrado fisico del disco
                        if os.path.exists(ruta_a_borrar):
                            os.remove(ruta_a_borrar)

                        #Registro y limpieza de las listas
                        self.nombres_archivos_eliminados.append(nombre_a_borrar)
                        self.rutas_archivos.pop(0)
                        self.nombres_archivos.pop(0)


                    #Guardamos la ruta unica
                    self.rutas_archivos.append(tmp.name)
                    #Guardamos el nombre original solo para mostrarlo
                    self.nombres_archivos.append(file.name)
                    self.cargados += 1
            
            # Captura errores inesperado
            except Exception as e:
                yield rx.window_alert("Ocurrió un error inesperado al procesar el archivo.")  

        if len(self.nombres_archivos_eliminados) > 0:
            yield rx.toast(f"El maximo son 3 por lo que se han borrado los siguientes archivos: {[e for e in self.nombres_archivos_eliminados]}")
        
        #Como ya no guardamos los archivos hacemos que tarde para que se vea la barra
        time.sleep(1.5)
        #Que siempre termine la barra y con el yield avisamos
        self.barra = False
        yield rx.toast(f"Se cargaron: {self.cargados} archivos con éxito")
    
    #Metodo que usa los botones con un rx.toast
    def borrar_datos(self):
        self.borrar_datos_limpio()
        return rx.toast("Todos los archivos han sido eliminador")
    
    #Metodo para borrar los archivos de la sesion
    def borrar_datos_limpio(self):
            for ruta in self.rutas_archivos:
                try:
                    if os.path.exists(ruta):
                        os.remove(ruta)
                        print(f"Archivo eliminado: {ruta}")
                except Exception as e:
                    print(f"Error borrando {ruta}: {e}")

            #Limpiamos las listas del estado
            self.rutas_archivos = []
            self.nombres_archivos_eliminados = []
            self.nombres_archivos_eliminados = self.nombres_archivos
            self.nombres_archivos = []
            if len(self.nombres_archivos_eliminados) != 0:
                print(f"Todos los archivos borrados: {[e for e in self.nombres_archivos_eliminados]}")

    #Le dice a Python que la funcion pertenece a la clase pero no necesita una "instancia" para ejecutarse.
    @staticmethod
    #Metodo que borra archivos con mas de 24 horas
    def limpieza_inteligente_csv():
        #Ruta de la carpeta temporal
        ruta_temporal = tempfile.gettempdir()
        
        #Limite de tiempo (24 horas en segundos)
        un_dia_en_segundos = 24 * 60 * 60
        ahora = time.time()
        
        #Buscamos todos los archivos .csv
        patron = os.path.join(ruta_temporal, "*.csv")
        archivos_csv = glob.glob(patron)
        
        print(f"--- Iniciando limpieza inteligente en: {ruta_temporal} ---")
        
        for archivo in archivos_csv:
            try:
                #Obtenemos la fecha de la ultima modificacion del archivo
                fecha_archivo = os.path.getmtime(archivo)
                antiguedad = ahora - fecha_archivo
                
                #Solo borramos si el archivo tiene mas de 24 horas
                if antiguedad > un_dia_en_segundos:
                    os.remove(archivo)
                    print(f"Eliminado (Antiguo): {os.path.basename(archivo)}")
                else:
                    # Opcional: imprimir qué archivos se conservan
                    print(f"Conservado (Reciente): {os.path.basename(archivo)}")
                    
            except Exception as e:
                print(f"No se pudo procesar {archivo}: {e}")
                            
    #Definimos este metodo como evento de Reflex que se ejecuta en segundo plano
    @rx.event(background=True)
    #Definimos el metodo como asincrono permitiendo que el servidor haga otras tareas mientras tanto 
    async def loop_monitor_conexion(self):
        #Importacion local para evitar errores circulares
        import TFG_2026_Nicolas_Garcia_Gomez.TFG_2026_Nicolas_Garcia_Gomez as main_file
        
        #Obtenemos la instancia de la app que creaste con rx.App()
        #Si aun no se ha creado, devuelve None en lugar de dar un error, gracias a getattr.
        app_instance = getattr(main_file, "app", None)

        #Guarda el identificador unico de la sesion. Si la pestaña se cierra, ese token desaparece(es un DNI)
        token = self.router.session.client_token
        
        print(f"WATCHDOG INICIADO PARA: {token}", flush=True)

        while True:
            #Si por algun motivo la app no cargo a la primera lo reintentamos
            if app_instance is None:
                app_instance = getattr(main_file, "app", None)
                print("Esperando instancia de la App...", flush=True)

                #Si la aplicacion no esta lista, espera 2 segundos y vuelve a empezar el bucle.
                await asyncio.sleep(2)
                continue

            #Verificamos si el token sigue en la lista de conexiones activas
            #Si el token no esta en token_to_sid, la conexion se cerro
            if token not in app_instance.event_namespace.token_to_sid:
                print(f"DESCONEXIÓN DETECTADA: {token}", flush=True)
                
                #Como esta funcion corre en segundo plano, Reflex prohibe modificar variables directamente. 
                #Este bloque "pide permiso" al estado para poder entrar y hacer cambios de forma segura.
                async with self:
                    #Borramos tanto los archivos del usuario como los residuos de mas de 24 horas
                    self.borrar_datos_limpio()
                    self.limpieza_inteligente_csv()
                
                #Una vez que el usuario se ha ido, el guardian ya no es necesario.
                break  

            #Espera 5 segundos entre cada comprobacion
            await asyncio.sleep(5)