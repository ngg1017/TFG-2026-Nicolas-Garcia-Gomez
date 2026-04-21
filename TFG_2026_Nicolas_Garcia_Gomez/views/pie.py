import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, TextoColor
import TFG_2026_Nicolas_Garcia_Gomez.constantes as constantes

def pie() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(
                "Indicadores de calidad de la URCCPQ",
                size = "2"
                ),

            rx.link(
                "Creado por Nicolas Garcia Gomez un estudiante de Ingenieria de la salud",
                size = "2",
                color = TextoColor.TERCIARIO.value,
                href = constantes.ING_SALUD,
                is_external = True
            ),

            align = "start",
            spacing = "0"
        ),

        #Ocupa todo el espacio mandando la imagen a la derecha
        rx.spacer(),
        rx.image(
            src = "ubu.png",
            alt = "Logo de la universidad de Burgos",
            width = Size.MUYGRANDE.value
            
        ),
        padding_button = Size.GRANDE.value,
        style = estilos.max_width_estilo,
    )
