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
                    "Esta herramienta clínica permite el análisis de datos a través de dos vías: la extracción automática desde la ",
                    rx.text("Base de Datos", weight="bold", as_="span"),
                    " integrada, o mediante la carga tradicional de archivos locales.",
                    as_="span"
                ),
                rx.text(
                    "Si opta por la carga manual, es necesario suministrar archivos en formato CSV. Si la recolección de los datos se realizó en un archivo Excel (.xlsx), " \
                    "se requiere su conversión previa. Se facilita un enlace externo para este proceso: ",
                    rx.link(
                        "Excel a CSV", 
                        href = constantes.EXCEL_A_CSV, 
                        is_external = True, 
                        color = TextoColor.ACENTO.value
                    ),
                    as_="span"
                ),
                rx.text(
                    "En caso de necesitar auditar o editar un archivo CSV histórico fuera del aplicativo, lo más común es usar Excel. Para visualizarlo correctamente: ",
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