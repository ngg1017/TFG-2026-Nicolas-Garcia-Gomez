import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
from TFG_2026_Nicolas_Garcia_Gomez.componentes.boton_subida import boton_subida
from Logica.State import State
from Logica.Programa import Programa
from Logica.Usuarios import Usuarios
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
                "* Es necesaria la subida de archivos en formato ",
                rx.text(
                        "formato CSV ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                "a través del botón/zona de arrastre ",
                rx.text(
                        "'Carga de archivos'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                ", tras lo cual aparecerá una barra de carga. Luego de su finalización estarán listos para ser procesados.",
                as_="span"
            ),

            rx.text(
                    "* Posteriormente es necesario presionar el botón ",
                    rx.text(
                        "'Selección de Indicadores'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ". Este nos permitirá seleccionar el indicador que se desee o inclusive procesar el resumen de todos ellos a través de ",
                    rx.text(
                        "'Resumen Indicadores'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    ".",
                    as_="span"
            ),

            rx.text(
                "* Una vez seleccionado el indicador se podrá visualizar un gráfico de barras o de área, ambos representan la evolución temporal y la " \
                "tendencia histórica de los indicadores clínicos, evaluando visualmente su estabilidad mediante márgenes de variabilidad interanual. " \
                "Además, existe la posibilidad de descargar los cálculos relizados cada año gracias al botón de ",
                rx.text(
                        "'Descargar'",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                ". En caso del resumen se permitirá descargar el informe final por medio del pulsador ",
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
                        State.rutas_archivos.length() > 0,
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
                #Condicional que permite controlar el acceso a los diferentes roles
                rx.cond(
                    Usuarios.rol == 3,
                    rx.vstack(
                        rx.button("Carga de Datos desde la BBDD", on_click=BBDD.abrir_consulta),
                        rx.button("Acceso a la BBD"),
                        rx.button("Exportacion archivos en CSV"),
                        align="center",
                        spacing="4"
                    ),
                    rx.cond(
                        Usuarios.rol == 2,
                        rx.vstack(
                            rx.button("Carga de Datos desde la BBDD", on_click=BBDD.abrir_consulta),
                            rx.button("Acceso a la BBD"),
                            align="center",
                            spacing="4"
                        ),
                        rx.button("Carga de Datos desde la BBDD", on_click=BBDD.abrir_consulta)
                    )
                ),
                #Añadimos un id para poder ir con rx.scroll_to
                id="zona_de_carga",
                width="100%", 
                margin_bottom=Size.PEQUEÑO.value,
                spacing="9"
            ),
            
            #Centra el boton para seleccionar los condicionantes
            rx.cond(
                State.rutas_archivos.length() > 0,
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