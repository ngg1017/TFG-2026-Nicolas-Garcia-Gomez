import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor

def cabecera() -> rx.Component:
    return rx.vstack(

        #Cabecera
        rx.heading(      
            "Indicadores de calidad REA",
            size = "9",

            #Para dejar espacios con los bordes
            padding_buttom = Size.DEFECTO.value
        ),
        #Para estructurar el contenido
        rx.flex(          
            rx.image(
                src = "sacyl.png",
                alt = "Icono de Sacyl",
                width = "16em",
                height = "16em",
                margin_right = Size.GRANDE.value 
            ),
            rx.vstack(
                
                #Agrupa y organiza otros componentes
                rx.box(

                    #Las lineas superiores
                    rx.text("Instrucciones de Carga"),
                    rx.text("Por favor seguir los pasos descritos a continuación")
                ),

                #Hay que ponerles as_ para que no fuerzen un salto de línea
                rx.text(
                    "Para poder ver los indicadores de calidad debe clicar en el boton de ",

                    #Subtexto en color rojo
                    rx.text(
                        "'Subir archivo' de color rojo",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    "!.",
                    as_="span"
                ),
                rx.text(
                    "Una vez clique en el boton debe seleccionar el archivo de texto en ",
                    rx.text(
                        "formato CSV(muy importante) ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    "y con los nombres de las columnas especificados.",
                    as_="span"
                ),
                rx.text(
                    "Cuando este todo cargado solo tienes que seleccionar en el desplegable el indicador deseado.",
                    as_="span"
                ),
                rx.link(
                    "UbU",
                    href = "https://www.ubu.es/",
                    is_external = True,
                    color = TextoColor.TERCIARIO.value,
                    padding_top = Size.GRANDE.value,
                    font_size = Size.MEDIANO.value
                )
            )
        )
    )