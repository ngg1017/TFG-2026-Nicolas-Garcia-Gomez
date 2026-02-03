import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import ESTILO_BASE

#Para crear botones
def link_icon(icon: str, url: str) -> rx.Component:
    return rx.link(                                   #Creamos el link
        rx.button(
            icon,
            class_name="btn btn-lg",                  #Importamos de Boostrap el boton
            size = "4"
        ),
        href = url,                                   #El link que abrimos
        is_external = True                            #Hacemos que se abrea en una ventana nueva
    )