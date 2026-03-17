import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
from TFG_2026_Nicolas_Garcia_Gomez.componentes.boton_subida import boton_subida
from Logica.State import State
from TFG_2026_Nicolas_Garcia_Gomez.componentes.seleccion import seleccion

def instrucciones() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                "¿Como funciona esta herramienta?",
                class_name="title",
                color = TextoColor.ACENTO.value
            ),

            rx.text(
                "* Lo primero de todo tienes que tener unos datos aninizadas aunque como esta herramienta es local no habría ningun problema en que no lo esten",
                as_="span"
            ),

            rx.text(
                    "* Tienes que presionar el boton que dice 'Carga de archivos' y cerciorarte de que los datos estan en ",
                    rx.text(
                        "formato CSV ",
                        color = Color.ACENTO.value,
                        as_="span"
                    ),
                    "esto es muy importanto por lo que tienes que tener mucho cuidado.",
                    as_="span"
            ),

            rx.text(
                "* No te preocupes si salta algun error el 99% de ellos es debido a una columna mal nombrada, esta aplicacion te devuelve el nombre de la columna que espera y en que calculo se recibe",
                as_="samp"
            ),
            
            rx.center(
                rx.hstack(
                    rx.text("Archivos cargados: "),

                    #Muestra todos los archivos cargados
                    rx.foreach(
                        State.nombres_archivos,
                        lambda nombre: rx.text(f"{nombre} ", color = TextoColor.ACENTO.value)
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
                    
                    align="center", 
                ),
                width="100%",
                margin_top=Size.MEDIANO.value
            ),
            
            #Condicional que si State.barra es True aparezca la barra de carga(rx.progress) sino solo un espacio
            rx.cond(
                State.barra,
                rx.vstack(
                    rx.text("Procesando archivos..."),
                    rx.progress(is_indeterminate=True, width="100%"),
                    width="100%",
                    padding_top="1em",
                ),
                # Si no está cargando, pone un espacio vacío
                rx.spacer()
            ),
            
            #Centra el boton de subida
            rx.center(                      
                boton_subida("Carga de archivos"),
                width="100%", 
                margin_bottom=Size.PEQUEÑO.value
            ),
            
            #Centra el boton para seleccionar los condicionantes
            rx.cond(
                State.rutas_archivos.length() > 0,
                rx.center(
                seleccion("Seleccion de indicadores"),
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