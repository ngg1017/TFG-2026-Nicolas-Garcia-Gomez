import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
from TFG_2026_Nicolas_Garcia_Gomez.componentes.boton_subida import boton_subida
from Logica.State import State
from Logica.Programa import Programa
from Logica.BBDD import BBDD
from TFG_2026_Nicolas_Garcia_Gomez.componentes.seleccion import seleccion

def instrucciones() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                "¿Cómo funciona esta herramienta?",
                class_name="title",
                color = TextoColor.ACENTO.value
            ),

            rx.text(
                "* El análisis comienza definiendo el origen de la información. Puede sincronizar los registros directamente desde la ",
                rx.text(
                        "Base de Datos ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                "utilizando el botón ",
                rx.text(
                        "'Apertura de la BBDD' ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                "o, de manera alternativa, arrastrando archivos en ", 
                rx.text(
                        "formato CSV ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                "a la zona de ",
                rx.text(
                        "'Carga de archivos'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                ". Una vez completada la barra de progreso, los datos estarán en memoria listos para ser procesados.",
                as_="span"
            ),

            rx.text(
                    "* Posteriormente es necesario presionar el menú ",
                    rx.text(
                        "'Selección de Indicadores'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ". Este nos permitirá seleccionar el indicador individual que se desee analizar o inclusive procesar el consolidado de todos ellos a través de ",
                    rx.text(
                        "'Resumen Indicadores'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ".",
                    as_="span"
            ),

            rx.text(
                "* Tras el cálculo, se generará una visualización interactiva (gráfico de barras o área) que representa la evolución temporal y la " \
                "tendencia histórica de los indicadores clínicos, evaluando visualmente su estabilidad mediante márgenes de variabilidad interanual. " \
                "Además, existe la posibilidad de extraer las tablas de resultados mediante el botón ",
                rx.text(
                        "'Descargar'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                ". En el caso del resumen global, se habilitará la generación de un documento en PDF por medio del pulsador ",
                rx.text(
                        "'Descargar Informe'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                ".",
                as_="samp"
            ),
            
            rx.center(
                rx.flex(
                    rx.text("Archivos cargados: "),

                    #Muestra todos los archivos cargados
                    rx.foreach(
                        Programa.nombres_archivos,
                        lambda nombre:rx.text(f"{nombre} ", color = TextoColor.ACENTO.value, size="2"),
                    ),

                    #Condicional para cuando existan documentos aparezca el boton de borrar
                    rx.cond(
                        State.nombres_archivos.length() > 0,
                        rx.button(
                            "Borrar",
                            size = "2",
                            font_size = "13px",
                            on_click= State.borrar_datos,
                            style={"margin_bottom": "14.5px"},
                        ),
                        rx.spacer()
                    ),
                    #Permite que los elementos pasen a la siguiente fila
                    flex_wrap="wrap", 
                    #Alinea verticalmente el texto y el boton en cada fila         
                    align_items="center",  
                    #Mantiene todo el grupo centrado    
                    justify_content="center",
                    #Espacio uniforme entre elementos 
                    spacing="2",               
                    width="100%",
                ),
                width="100%",
                margin_top=Size.MEDIANO.value
            ),
            
            #Condicional que si State.barra es True aparezca la barra de carga(rx.progress) sino solo un espacio
            rx.cond(
                State.barra,
                rx.vstack(
                    rx.text("Procesando archivos..."),
                    rx.progress(is_indeterminate=False, width="100%"),
                    width="100%",
                    padding_top="1em",
                ),
                # Si no está cargando, pone un espacio vacío
                rx.spacer()
            ),
            
            #Centra el boton de subida
            rx.center(                      
                boton_subida("Carga de archivos"),
                rx.button("Apertura de la BBDD", on_click=BBDD.abrir_consulta),
                #Añadimos un id para poder ir con rx.scroll_to
                id="zona_de_carga",
                width="100%", 
                margin_bottom=Size.PEQUEÑO.value,
                spacing="9"
            ),
            
            #Centra el boton para seleccionar los condicionantes
            rx.cond(
                State.nombres_archivos.length() > 0,
                rx.center(
                seleccion("Selección de Indicadores"),
                width="100%",
                margin_top=Size.PEQUEÑO.value,
                margin_bottom=Size.GRANDE.value
                ),
                rx.spacer()
            ),

            #Le ponemos un recuadro de bootstrap
            width = "100%",
            class_name = "container-fluid border border-red rounded"
        ),
        style=estilos.max_width_estilo
    )