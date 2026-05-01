import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
import TFG_2026_Nicolas_Garcia_Gomez.constantes as constantes

def cabecera() -> rx.Component:
    return rx.vstack(

        #Titulo
        rx.heading(      
            "Indicadores de calidad URCCPQ",
            size = "9",

            #Para dejar espacios con los bordes
            padding_buttom = Size.DEFECTO.value,
            margin_x = "auto"
        ),

        #Para estructurar el contenido
        rx.flex(          
            rx.image(
                src = "urccpq.png",
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
                    rx.text("Vamos a desgranar cómo funciona y qué ventajas proporciona al usuario.",
                            size = "6"
                    ),
                    class_name = "container-fluid border border-red rounded"
                ),

                #Hay que ponerles as_ para que no fuerzen un salto de línea
                rx.text(
                    "Esta herramienta va a utilizarse para la creación de ",

                    #Subtexto en color rojo
                    rx.text(
                        "Indicadores de calidad",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ". Gracias a los archivo en formato ",
                    rx.link(
                        "CSV", 
                        href = constantes.CSV, 
                        is_external = True, 
                        color = TextoColor.ACENTO.value
                    ),
                    ".",
                    as_="span"
                ),
                rx.text(
                    "Como se ha comentado esta herramienta se nutre de archivos CSV. Ante cualquier complicación que puediera surgir con el " \
                    "tratamiento de dichos archivos, se dejan una serie de enlaces para dominar su uso.",
                    as_="span"
                ),
                rx.text(
                    "Para la recolección de los datos es aconsejable utilizar un archivo .xlsx o archivo Excel. Posteriormente es necesaria su conversión " \
                    "al formato correspondiente. Se deja un enlace externo para facilitar el proceso: ",
                    rx.link(
                        "Excel a CSV", 
                        href = constantes.EXCEL_A_CSV, 
                        is_external = True, 
                        color = TextoColor.ACENTO.value
                    ),
                    as_="span"
                ),
                rx.text(
                    "Si se dispone de un archivo CSV y el objetivo es editarlo, lo más común es usar Excel." \
                    " Para poder visualizar correctamente un archivo CSV en Excel: ",
                    rx.link(
                        "CSV a EXCEL", 
                        href = constantes.CSV_A_EXCEL, 
                        is_external = True, 
                        color = TextoColor.ACENTO.value
                    ),
                    as_="span"
                )
            ),
            #Establece direcciones en diferentes tamaños de pantalla
            direction = {"sm": "column","md": "column","lg": "row",}
        ),
        style = estilos.max_width_estilo,
        padding_top = Size.GRANDE.value
    )