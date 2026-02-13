import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color
from Logica.Programa import Programa
from Practicas_2026_Nicolas_Garcia_Gomez.componentes.graf_barras import graf_barras

"""
Ajustar texto a la izquierda
"""

#Devulve la ventana flotante
def vent_flotante(texto: str, datos: list[dict]) -> rx.Component:

    #Ventana flotante
    return rx.dialog.root(
        #Contenido de la ventana
        rx.dialog.content(

            #Titulo
            rx.vstack(
                rx.dialog.title(
                    texto.split(":")[0],
                    weight="bold",
                    color = TextoColor.ACENTO.value,

                    #Para que no empuge la ventana
                    white_space="nowrap"
                ),
                align="center"
            ),

            rx.vstack(
                #El texto de cada indicador
                rx.text(
                    texto.split(":")[1], 
                    width="auto", 
                    text_align="center"
                ),
                rx.cond(
                    #Condicional para que en el indicador por especialidad no salgan las tarjetas
                    Programa.ind_especi,
                    rx.spacer(),
                    rx.hstack(
                        #Creamos una card por cada archivo guardado
                        rx.foreach(
                            datos,
                            lambda item: rx.card(
                                rx.vstack(
                                    rx.text(
                                        f"El año: {item["name"]}",
                                        align="center"
                                    ),
                                    rx.text(
                                        f"Tuvimos: {item["valor"]}",
                                        align="center"
                                    ),
                                    align="center",
                                    justify="center",
                                    spacing="2",
                                ),
                                style={
                                    "border": f"2px solid {Color.ACENTO.value}"
                                }
                            )  
                        ),
                        flex_wrap="wrap",
                        justify="center",
                        spacing="4",
                    )
                ),
                #Llamamos al grafico
                graf_barras(datos, Programa.ind_especi),
                align="center",
                spacing="4",
            ),

            #Descargar los datos filtrados
            rx.hstack(
                #Creamos un boton por cada archivo para descargar
                rx.foreach(
                    datos,
                    lambda item, i: rx.button(
                        f"Descargar {item["name"]}",
                        on_click=Programa.descargar_archivo(i)
                    )
                    
                ),
                justify = "center",
                flex_wrap="wrap",
                spacing="2"
            ),
        
            #Para cerrar la ventana
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Cerrar",
                        on_click=Programa.cerrar_ventana,
                        margin_top = "10px"
                    )
                ),
                width="100%"
            ),
            
            #Permite que el ancho crezca segun el contenido
            z_index="2000",
            width="fit-content", 
            #Eliminamos los limites de tamaño permitiendo que se expanda segun la necesidad
            max_width="67vw",
            padding="2em",
        ),
        #Mostar solo cuando se haya hecho un calculo(se selecciona una opcion)
        open=Programa.mostrar_resultado,
    )