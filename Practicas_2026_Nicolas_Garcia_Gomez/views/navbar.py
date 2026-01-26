import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color
from Practicas_2026_Nicolas_Garcia_Gomez.componentes.link_icon import link_icon
import Practicas_2026_Nicolas_Garcia_Gomez.constantes as constantes

#Creamos la barra lateral
def navbar() -> rx.Component:
    return rx.vstack(                                     #Linea debajo de la barra vertical
        rx.hstack(                                        #Crea la barra en horizontal
            rx.image(                                     #Para poner imagen a la barra
                src = "sacyl.png",
                alt = "Icono del sacyl",
                width = Size.MUYGRANDE.value,
                height = Size.MUYGRANDE.value
            ),
            rx.text(f"Indicadores Calidad", size = "5"),  #Texto de la barra
            rx.spacer(),                                  #Empuja la barra a la izquierda
            link_icon(                                    #Creamos el boton en la navbar
                "Pagina web REA", 
                constantes.REA_URL
            ),
            width = "100%",                               #Tamaño de la barra(ocupa la totalidad)
            align="center"
        ),
        position = "sticky",                                           #Hace que la linea debajo siempre este fija
        bg = Color.PRIMARIO.value,                                     #Color de fondo
        border_bottom = f"0.25em solid {Color.SECUNDARIO.value}",      #Aparezca la linea de debajo
        padding_x = Size.GRANDE.value,                                 #Separa icono de las letras
        padding_y = Size.DEFECTO.value,
        z_index = "999",                                               #Siempre esta la primera
        top = "0",                                                     #Se pegue a la parte superior
    )
