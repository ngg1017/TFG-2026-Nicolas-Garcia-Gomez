import reflex as rx
from .fuentes import Fuente as Fuente
from .colores import TextoColor, Color
from enum import Enum

MAX_WIDTH = "1000px"

#Definimos los tamaños que vamos a usar em va en consonancia con la fuente
class Size(Enum):
    ZERO = "0px"
    PEQUEÑO = "0.5em"
    MEDIANO = "0.8em"
    DEFECTO = "1em"
    GRANDE = "2em"
    MUYGRANDE = "6em"


#Hoja de estilos donde esta la fuente de google fonts y los elementos graficos(la primera)
HOJAESTILO = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
    "https://fonts.googleapis.com/css?family=Roboto&display=swap"
]

#Creamos la base de la fuente, el color y el fondo
ESTILO_BASE = {
    "font_family": Fuente.defecto.value,
    "color" : TextoColor.PRIMARIO.value,
    "background": Color.PRIMARIO.value,
    
    rx.heading: {
        "color": TextoColor.OSCURO.value,
        "font_family": Fuente.defecto.value,
        "text_shadow": "0px 0px 3px rgba(255, 255, 255, 0.8)",
    },
    
    rx.link: {
        "text_decoration": "none",
        "justify": "center",
        "align": "center"
    },

    rx.button: {
        "class_name":"btn btn",
        "color": TextoColor.PRIMARIO.value,
        "bg": Color.OSCURO.value,
        "borderRadius": "0.75rem",
        "weight": "bold",
        "justify": "center",
        "align": "center",
        "_hover": {
                "bg": Color.ACENTO.value,
                "color": TextoColor.SECUNDARIO.value
        }
    }
}

max_width_estilo = dict(
    align = "center",
    justify = "center",
    padding_x = Size.GRANDE.value,
    width = "100%",
    max_width = MAX_WIDTH,
    #el contenido de la página es más ancho, el vstack se pegará a la izquierda por lo que ponemos el margin
    margin_x = "auto" 
)