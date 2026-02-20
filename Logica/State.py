import reflex as rx
import os
import tempfile
import time

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
                    print(tmp.name)

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
    
    def borrar_datos(self):
        #Borramos los archivos fisicos uno por uno
        for ruta in self.rutas_archivos:
            if os.path.exists(ruta):
                os.remove(ruta)

        #Limpiamos las listas del estado
        self.rutas_archivos = []
        self.nombres_archivos_eliminados = []
        self.nombres_archivos_eliminados = self.nombres_archivos
        self.nombres_archivos = []
        if len(self.nombres_archivos_eliminados) != 0:
            return rx.toast(f"Todos los archivos borrados: {[e for e in self.nombres_archivos_eliminados]}")

        
        
