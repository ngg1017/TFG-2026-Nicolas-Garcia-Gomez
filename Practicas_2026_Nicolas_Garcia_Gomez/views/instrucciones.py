import reflex as rx
import Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos import Size, Color, TextoColor
from Practicas_2026_Nicolas_Garcia_Gomez.componentes.boton import boton_subida
from Logica.State import State

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
            rx.text(
                State.documentos.length(),
                State.nombres_archivos,
                as_="samp"
            ),
            rx.center(
                boton_subida(
                    "Carga de archivos",
                ),
                width="100%", 
                margin_bottom=Size.MEDIANO.value
            ),

            width = "100%",
            class_name = "container-fluid border border-red rounded"
        ),
        style=estilos.max_width_estilo
    )