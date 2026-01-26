import reflex as rx
from .fuentes import Fuente as Fuente
from .colores import TextoColor, Color
from enum import Enum

#Definimos los tamaños que vamos a usar em va en consonancia con la fuente
class Size(Enum):
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
    "background": Color.PRIMARIO.value
}