import reflex as rx
import Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size
from Practicas_2026_Nicolas_Garcia_Gomez.views.navbar import navbar
from Practicas_2026_Nicolas_Garcia_Gomez.views.cabecera import cabecera

#Colocamos los elementos de la web
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                cabecera(),
                cabecera(),
                cabecera(),
                width = "100%",
                spacing = "9"
            )
        )
    )

#Establecemos los estilos
app = rx.App(
    stylesheets = estilos.HOJAESTILO,
    style = estilos.ESTILO_BASE
)

#Titulo y descripcion de la web
app.add_page(
    index,               #Le añadimos un indice
    title = "Indicadores de calidad REA",
    description = "Explciar como subir todos los componentes"
)




