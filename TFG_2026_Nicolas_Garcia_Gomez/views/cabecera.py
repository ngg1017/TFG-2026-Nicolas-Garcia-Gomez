import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
import TFG_2026_Nicolas_Garcia_Gomez.constantes as constantes

def cabecera() -> rx.Component:
    return rx.vstack(

        #Titulo
        rx.heading(      
            "Indicadores de calidad REA",
            size = "9",

            #Para dejar espacios con los bordes
            padding_buttom = Size.DEFECTO.value,
            margin_x = "auto"
        ),

        #Para estructurar el contenido
        rx.flex(          
            rx.image(
                src = "rea.png",
                alt = "Icono de Sacyl",
                width = "25em",
                height = "16em",
                margin_right = Size.GRANDE.value 
            ),
            rx.vstack(
                
                #Agrupa y organiza otros componentes
                rx.box(

                    #Las lineas superiores
                    rx.text("¡Bienvenido a esta herramienta!",
                            size = "6"
                    ),
                    rx.text("Vamos a desgranar como funciona y que ventajas vamos a tener con ella",
                            size = "6"
                    ),
                    class_name = "container-fluid border border-red rounded"
                ),

                #Hay que ponerles as_ para que no fuerzen un salto de línea
                rx.text(
                    "Esta herramienta va a utilizarse para la creacion de ",

                    #Subtexto en color rojo
                    rx.text(
                        "Indicadores de calidad",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ". Gracias a unos datos que vamos a obtener desde la dirección y vamos a procesar pero de momento no te procupes en como subirlos.",
                    as_="span"
                ),
                rx.text(
                    "Esta aplicación es muy sencilla por lo que no te sientas ",
                    rx.text(
                        "abrumad@",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ".",
                    as_="span"
                ),
                rx.text(
                    "Solo tienes que seguir las indicaciones del apartado de debajo y todo será muy fácil por lo que ¡Manos a la obra!.",
                    as_="span"
                ),
                rx.link(
                    "UbU",
                    href = constantes.UBU,
                    is_external = True,
                    color = TextoColor.TERCIARIO.value,
                    padding_top = Size.GRANDE.value,
                    font_size = Size.DEFECTO.value
                )
            ),
            #Establece direcciones en diferentes tamaños de pantalla
            direction = {"sm": "column","md": "column","lg": "row",}
        ),
        style = estilos.max_width_estilo,
        padding_top = Size.GRANDE.value
    )