#Posible implementacion de todas las columnas a utilizar vere si lo implemento aqui o en los propios métodos
# if "APACHE" not in df.columns:
    #raise ValueError(f"Falta la columna 'APACHE (0-71)' en {file.name}")
                
#Para desconvertirlo
#df = pd.DataFrame(self.documentos[0])

import reflex as rx
import pandas as pd
import io

class State(rx.State):
    documentos: list[list[dict]]
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

        for file in files:
            try: 
                upload_data = await file.read()

                #Convertimos a un "archivo virtual" en memoria y luego a Pandas
                #Usamos io.BytesIO para que Pandas pueda leerlo como si fuera un archivo físico
                df = pd.read_csv(io.BytesIO(upload_data))

                #Convertir a lista de diccionarios (Serializable)
                #Esto evita el error "dispatch is not a function"
                datos_serializables = df.to_dict(orient="records")

                #Impide que se guarden mas de 3
                while len(self.documentos) + 1 > 3:
                    self.documentos.pop(0)
                    self.nombres_archivos_eliminados.append(self.nombres_archivos[0])
                    self.nombres_archivos.pop(0)

                self.documentos.append(datos_serializables)
                self.nombres_archivos.append(file.name)
                self.cargados += 1

            except pd.errors.EmptyDataError:
                yield rx.window_alert(f"El archivo {file.name} está vacío.")
            
            # Captura cualquier otro error inesperado
            except Exception as e:
                #Imprime en la consola
                print(f"Error crítico: {e}") 
                yield rx.window_alert("Ocurrió un error inesperado al procesar el archivo.")

            finally:
                #Que siempre termine la barra y con el yield avisamos
                self.barra = False
                yield

        if len(self.nombres_archivos_eliminados) > 0:
            yield rx.toast(f"El maximo son 3 por lo que se han borrado los siguientes archivos: {[e for e in self.nombres_archivos_eliminados]}")
        
        yield rx.toast(f"Se cargaron: {self.cargados} archivos con éxito")
    
    def borrar_datos(self):
        self.nombres_archivos_eliminados = []
        self.nombres_archivos_eliminados = self.nombres_archivos
        self.documentos = []
        self.nombres_archivos = []
        yield rx.toast(f"Todos los archivos borrados: {[e for e in self.nombres_archivos_eliminados]}")
        