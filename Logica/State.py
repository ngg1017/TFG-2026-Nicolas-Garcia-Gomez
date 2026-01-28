import reflex as rx
import pandas as pd
import io

class State(rx.State):
    documentos: list[list[dict]]
    nombres_archivos: list[str]

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            upload_data = await file.read()

            #Convertimos a un "archivo virtual" en memoria y luego a Pandas
            #Usamos io.BytesIO para que Pandas pueda leerlo como si fuera un archivo físico
            df = pd.read_csv(io.BytesIO(upload_data))

            #Convertir a lista de diccionarios (Serializable)
            #Esto evita el error "dispatch is not a function"
            datos_serializables = df.to_dict(orient="records")

            #Para convertirlo
            #df = pd.DataFrame(self.documentos[0])

            self.documentos.append(datos_serializables)
            self.nombres_archivos.append(file.name)

    def limpiar(self):
        self.documentos = []
        self.nombres_archivos = []