import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor

#Para crear botones
def link_icon(icon: str, url: str) -> rx.Component:
    return rx.link(                                   #Creamos el link
        f"{icon}",
        class_name = "btn btn-lg",                    #Importamos de Boostrap el boton
        href = url,                                   #El link que abrimos
        is_external = True,                           #Hacemos que se abrea en una ventana nueva
        weight = "bold",                              #Tipo y debajo tamaño
        size = "8",
        color = TextoColor.PRIMARIO.value,
        bg = Color.OSCURO.value,
        _hover = {
            "bg": Color.ACENTO.value,
            "color": TextoColor.SECUNDARIO.value
        }
    )