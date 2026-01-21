import reflex as rx
import Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from Practicas_2026_Nicolas_Garcia_Gomez.views.navbar import navbar
from programa_prueba import main


# class State(rx.State):
#     # Para guardar el resultado del proceso
#     resultado: str = ""

#     async def handle_upload(self, files: list[rx.UploadFile]):
#         for file in files:
#             # Leemos el contenido del archivo subido
#             upload_data = await file.read()
#             contenido = upload_data.decode("utf-8")
            
#             # Ejecutamos tu lógica programada
#             self.resultado = mi_procedimiento(contenido)


# def index():
#     return rx.vstack(
#         rx.upload(
#             rx.vstack(
#                 rx.button("Seleccionar Archivo", color_scheme="blue"),
#                 rx.text("Arrastra archivos aquí o haz click"),
#             ),
#             id="upload_file",
#             border="1px dotted rgb(107,99,235)",
#             padding="2em",
#         ),
#         rx.button(
#             "Ejecutar Procedimiento",
#             on_click=State.handle_upload(rx.upload_files(upload_id="upload_file")),
#         ),
#         rx.text(f"Resultado: {State.resultado}"),
#         spacing="5",
#     )

#Colocamos los elementos de la web
def index() -> rx.Component:
    return rx.box(
        navbar()
    )

#Establecemos los estilos
app = rx.App(
    stylesheets = estilos.HOJAESTILO,
    style = estilos.ESTILO_BASE
)

#Titulo y descripcion de la web
app.add_page(
    index,               #Le añadimos un indice
    title = "Web para poder ver los indicadores de la REA",
    description = "Explciar como subir todos los componentes"
)




