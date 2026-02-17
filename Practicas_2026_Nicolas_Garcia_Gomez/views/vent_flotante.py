import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color
from Logica.Programa import Programa
from Practicas_2026_Nicolas_Garcia_Gomez.componentes.graf_barras import graf_barras

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
                    text_align = "start"
                ),
                rx.cond(
                    #Condicional para que en el indicador por especialidad o el resumen no salgan las tarjetas
                    Programa.ind_especi | Programa.ind_resumen,
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
                        spacing="4"
                    )
                ),
                #Llamamos a los graficos o la tabla resumen
                rx.cond(
                    Programa.ind_resumen,

                    #La base de la tabla   
                    rx.table.root(
                        #Define la seccion superior(donde van los nombres de las columnas)
                        rx.table.header(
                            #Creamos una unica fila
                            rx.table.row(
                                #Recorre la lista de nombres de columnas, por cada nombre, crea una "celda de cabecera"
                                rx.foreach(
                                    Programa.columnas, 
                                    lambda col: rx.table.column_header_cell(col)
                                ),
                                border = "solid",
                                border_color = Color.ACENTO.value
                            )
                        ),
                        #Cuerpo de la tabla
                        rx.table.body(
                            #Recorre la lista principal de los datos cada elemento row representa una fila completa de datos
                            rx.foreach(
                                Programa.datos,

                                #Por cada fila encontrada, crea un componente de fila fisica en la tabla
                                lambda row: rx.table.row(

                                    #Ahora que estamos dentro de una fila, recorremos cada valor individual que hay en esa fila
                                    rx.foreach(row, lambda cell: rx.table.cell(cell))
                                )
                            ),
                            border = "solid",
                            border_color = Color.ACENTO.value
                        ),
                        #Le da un aspecto con fondo solido y bordes suaves
                        variant="surface",
                        size="1",         
                        width="100%",
                        margin_bottom="1em",
                        overflow="hidden"
                    ),
                    rx.vstack(
                        #Menu seleccion graficos
                        rx.vstack(
                            rx.menu.root(
                                rx.menu.trigger(
                                    rx.button(
                                        "Seleccionar Gráfico",
                                        variant="surface",
                                        width="100%",
                                    )
                                ),
                                rx.menu.content(
                                    rx.menu.item("Gráfico de barras"),
                                    z_index="500", 
                                    background_color=Color.ACENTO.value,
                                    color=TextoColor.SECUNDARIO.value,
                                )
                            ),
                            padding_bottom = "10px",
                            padding_top = "9px"
                        ),
                        graf_barras(datos, Programa.ind_especi),
                        align="center"
                    )
                ),
                align="center",
                spacing="4",
                padding = "7px"
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