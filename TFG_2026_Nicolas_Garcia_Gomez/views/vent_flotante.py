import reflex as rx
from Logica.Programa import Programa
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color
from TFG_2026_Nicolas_Garcia_Gomez.componentes.mezcla import mezcla
from TFG_2026_Nicolas_Garcia_Gomez.componentes.graficos import (graf_barras, graf_barras_vert, graf_area, graf_area_vert, 
                                                                      graf_lineas, graf_lineas_vert, graf_dispersion, graf_pie, graf_funnel)

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
                    Programa.ind_especi | Programa.ind_resumen | Programa.ind_mezcla,
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
                    rx.cond(
                        Programa.ind_mezcla,
                        mezcla(),
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
                                        rx.menu.item("Gráfico de Barras", on_click=Programa.cambiar_grafico("barras")),
                                        rx.menu.item("Gráfico de Barras Vertical", on_click=Programa.cambiar_grafico("barras_vert")),
                                        rx.menu.item("Gráfico de Area", on_click=Programa.cambiar_grafico("area")),
                                        rx.menu.item("Gráfico de Area Vertical", on_click=Programa.cambiar_grafico("vertical")),
                                        rx.menu.item("Gráfico de Lineas", on_click=Programa.cambiar_grafico("lineas")),
                                        rx.menu.item("Gráfico de Lineas Vertical", on_click=Programa.cambiar_grafico("lin_vert")),
                                        rx.menu.item("Gráfico de Dispersión", on_click=Programa.cambiar_grafico("dispersion")),
                                        rx.cond(
                                            Programa.ind_especi,
                                            [rx.menu.item("Gráfico Pie Chart", on_click=Programa.cambiar_grafico("pie")),
                                            rx.menu.item("Gráfico Funnel", on_click=Programa.cambiar_grafico("funnel"))],
                                            rx.spacer()
                                        ),
                                        z_index="500", 
                                        background_color=Color.ACENTO.value,
                                        color=TextoColor.SECUNDARIO.value,
                                    )
                                ),
                                padding_bottom = "10px",
                                padding_top = "9px"
                            ),
                            rx.match(
                                Programa.ind_grafico,
                                ("barras", graf_barras(datos, Programa.ind_especi)),
                                ("barras_vert", graf_barras_vert(datos, Programa.ind_especi)),
                                ("area", graf_area(datos, Programa.ind_especi)),
                                ("vertical", graf_area_vert(datos, Programa.ind_especi)),
                                ("lineas", graf_lineas(datos, Programa.ind_especi)),
                                ("lin_vert", graf_lineas_vert(datos, Programa.ind_especi)),
                                ("dispersion", graf_dispersion(datos, Programa.ind_especi)),
                                ("pie", graf_pie(datos)),
                                ("funnel", graf_funnel(datos)),
                                rx.text("Selecciona un gráfico para que se muestren"),
                            ),
                            align="center"
                        )
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