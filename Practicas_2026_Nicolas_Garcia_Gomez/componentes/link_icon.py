import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import ESTILO_BASE

#Para crear botones
def link_icon(icon: str, url: str) -> rx.Component:
    #Creamos el link
    return rx.link(                                   
        rx.button(
            icon,
            #Importamos de Boostrap el boton
            class_name="btn btn-lg",                  
            size = "4"
        ),
        #El link que abrimos
        href = url,
        #Hacemos que se abrea en una ventana nueva                                
        is_external = True                            
    )