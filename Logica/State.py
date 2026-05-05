import reflex as rx
import pandas as pd
import io
import asyncio


class State(rx.State):
    nombres_archivos: list[str]
    nombres_archivos_eliminados: list[str]
    cargados: int
    barra: bool = False

    #Variable oculta en RAM
    _dataframes_memoria: list[pd.DataFrame] = []

    async def handle_upload(self, files: list[rx.UploadFile]):
        self.cargados = 0
        self.nombres_archivos_eliminados = []

        #Conseguimos avisar para activar la barra de carga
        self.barra = True
        yield

        #Controlar que el maximo de archivos es 10
        if len(files) > 10:
            self.barra = False
            yield rx.window_alert("El maximo de archivos para subir a la vez son 10 csv") 
            return

        #Controla que los archivos solo sean de tipo csv
        for file in files:
            if file.name.split(".")[-1].lower() != "csv":
                self.barra = False 
                yield rx.window_alert("El tipo de archivo a subir es CSV") 
                return

        for file in files:  
            try: 
                #Leemos los bytes a la RAM
                contenido = await file.read()
                
                #Detectamos el separador leyendo la primera linea en memoria
                contenido_texto = contenido.decode("latin1")
                primera_linea = contenido_texto.split("\n")[0]
                separador_detectado = ";" if primera_linea.count(";") > primera_linea.count(",") else ","

                #Engañamos a Pandas: io.BytesIO disfraza los bytes de la RAM como si fueran un archivo
                df = pd.read_csv(io.BytesIO(contenido), sep=separador_detectado, encoding="latin1")

                #Impide que se guarden mas de 10 en memoria y borra el mas antiguo
                while len(self._dataframes_memoria) >= 10:
                    #Lo elimina de la RAM
                    self._dataframes_memoria.pop(0) 
                    nombre_a_borrar = self.nombres_archivos.pop(0)
                    self.nombres_archivos_eliminados.append(nombre_a_borrar)

                #Guardamos el DataFrame ya procesado
                self._dataframes_memoria.append(df)
                self.nombres_archivos.append(file.name)
                self.cargados += 1
        
            except Exception as e:
                yield rx.window_alert("Ocurrió un error inesperado al procesar el archivo.")  

        if len(self.nombres_archivos_eliminados) > 0:
            yield rx.toast(f"El maximo son 10 por lo que se han borrado los siguientes archivos: {[e for e in self.nombres_archivos_eliminados]}")
        
        #Hacemos que tarde para que se vea la barra (asincrono para no colgar)
        await asyncio.sleep(1.5)
        self.barra = False
        yield rx.toast(f"Se cargaron: {self.cargados} archivos en memoria con éxito")
    
    
    #Metodo que usa los botones con un rx.toast
    def borrar_datos(self):
        self.borrar_datos_limpio()
        return rx.toast("Todos los archivos han sido eliminador")
    
    def borrar_datos_limpio(self):
        #Al vaciar la lista, Python libera la memoria RAM automaticamente
        self._dataframes_memoria = []
        self.nombres_archivos_eliminados = self.nombres_archivos.copy()
        self.nombres_archivos = []
        if len(self.nombres_archivos_eliminados) != 0:
            print(f"Todos los archivos borrados de la RAM: {[e for e in self.nombres_archivos_eliminados]}", flush=True)

    def set_barra(self, valor: bool):
        self.barra = valor