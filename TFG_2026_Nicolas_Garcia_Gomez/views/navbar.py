import reflex as rx
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color
from TFG_2026_Nicolas_Garcia_Gomez.componentes.link_icon import link_icon
import TFG_2026_Nicolas_Garcia_Gomez.constantes as constantes
from Logica.Usuarios import Usuarios

#Creamos la barra lateral
def navbar() -> rx.Component:
    #Linea debajo de la barra vertical
    return rx.vstack(   
        #Crea la barra en horizontal                                  
        rx.hstack( 
            #Para poner imagen a la barra                                       
            rx.image(                                     
                src = "sacyl.png",
                alt = "Icono del sacyl",
                width = Size.MUYGRANDE.value,
                height = Size.MUYGRANDE.value
            ),
            #Texto de la barra
            rx.text(f"Indicadores Calidad", size = "5"), 
            
            rx.spacer(),
            rx.button(
                "Cerrar Sesión",
                on_click=Usuarios.cerrar_sesion,
                width="8%",
                height="auto",
                font_size="21px",
                padding="0.45em"
            ),
            
            #Empuja la barra a la izquierda
            rx.spacer(),
            #Creamos el boton en la navbar                               
            link_icon(                                    
                "Página web REA", 
                constantes.REA_URL
            ),
            #Tamaño de la barra(ocupa la totalidad)
            width = "100%",                               
            align="center"
        ),
        #Hace que la linea debajo siempre este fija
        position = "sticky",
        #Color de fondo                                           
        bg = Color.PRIMARIO.value,     
        #Aparezca la linea de debajo                                
        border_bottom = f"0.25em solid {Color.SECUNDARIO.value}", 
        #Separa icono de las letras     
        padding_x = Size.GRANDE.value,                                 
        padding_y = Size.DEFECTO.value,
        #Siempre esta por encima
        z_index = "10", 
        #Se pegue a la parte superior                                               
        top = "0",                                                    
    )
