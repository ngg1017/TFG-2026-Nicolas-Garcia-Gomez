import reflex as rx
from Logica.Programa import Programa
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color
from TFG_2026_Nicolas_Garcia_Gomez.componentes.mezcla import mezcla
from TFG_2026_Nicolas_Garcia_Gomez.componentes.tabla import tabla
from TFG_2026_Nicolas_Garcia_Gomez.componentes.graficos import (graf_barras, graf_barras_vert, graf_area, graf_area_vert, 
                                                                      graf_lineas, graf_lineas_vert, graf_dispersion, graf_pie, graf_funnel,
                                                                      graf_ar_mezcla, area_sync, composed, graf_pie_mezcla)

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
                    #Condicional para que en el indicador por especialidad, en el resumen y en la mezcla no salgan las tarjetas
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
                    rx.vstack(
                        rx.foreach(
                            Programa.lista_unida,
                            lambda lista: tabla(lista[0].to(list), lista[1].to(list))
                        )
                    ),
                    #Condicional anidado para separar los indicadores del metodo que permite mezclar
                    rx.cond(
                        Programa.ind_mezcla,
                        rx.vstack(
                            #Llama al metodo de mezclar
                            mezcla(),
                            #Condicional que permite esconder el boton de seleccion de graficos si no hay indicadores seleccionados
                            rx.cond(
                                Programa.lista_selecc.length() > 0,
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
                                            rx.menu.item("Gráfico de Area", on_click=Programa.cambiar_grafico("area")),
                                            rx.menu.item("Gráfico Compuesto Separado", on_click=Programa.cambiar_grafico("compuesto_1")),
                                            rx.menu.item("Gráfico Compuesto", on_click=Programa.cambiar_grafico("compuesto")),
                                            rx.menu.item("Gráfico Tarta", on_click=Programa.cambiar_grafico("pie")),
                                            rx.menu.item("", on_click=Programa.cambiar_grafico("compuesto")),
                                            z_index="500", 
                                            background_color=Color.ACENTO.value,
                                            color=TextoColor.SECUNDARIO.value,
                                        )
                                    ),
                                    padding_bottom = "10px",
                                    padding_top = "9px"
                                )
                            ),
                            rx.match(
                                Programa.ind_grafico,
                                ("area", graf_ar_mezcla(datos, Programa.lista_selecc)),
                                ("compuesto_1", area_sync(datos, Programa.lista_selecc)),
                                ("compuesto", composed(datos, Programa.lista_selecc)),
                                ("pie", graf_pie_mezcla(datos, Programa.lista_selecc)),
                                (" ", composed(datos, Programa.lista_selecc)),
                                #Condicional que nos permite ajustar el mensaje ya sea para seleccionar graficos o indicadores
                                rx.cond(
                                    Programa.lista_selecc.length() > 0,
                                    rx.text("Selecciona un gráfico para que se muestren"),
                                    rx.text("Seleccione un indicador para poder seleccionar los gráficos")
                                ),
                            ),
                            align="center"
                        ),
                        rx.vstack(
                            #Menu seleccion graficos
                            rx.vstack(
                                rx.menu.root(
                                    #Boton para abrir el desplebagle
                                    rx.menu.trigger(
                                        rx.button(
                                            "Seleccionar Gráfico",
                                            variant="surface",
                                            width="100%",
                                        )
                                    ),
                                    #Menu desplegable, sus opciones ejcutan el metodo cambiar_grafico con su grafico correspondiente
                                    rx.menu.content(
                                        rx.menu.item("Gráfico de Barras", on_click=Programa.cambiar_grafico("barras")),
                                        rx.menu.item("Gráfico de Barras Vertical", on_click=Programa.cambiar_grafico("barras_vert")),
                                        rx.menu.item("Gráfico de Area", on_click=Programa.cambiar_grafico("area")),
                                        rx.menu.item("Gráfico de Area Vertical", on_click=Programa.cambiar_grafico("vertical")),
                                        rx.menu.item("Gráfico de Lineas", on_click=Programa.cambiar_grafico("lineas")),
                                        rx.menu.item("Gráfico de Lineas Vertical", on_click=Programa.cambiar_grafico("lin_vert")),
                                        rx.menu.item("Gráfico de Dispersión", on_click=Programa.cambiar_grafico("dispersion")),
                                        #Condicional para mostrar graficos nuevos en el ind por especialidades
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
                            #Este match nos permite mostrar el grafico seleccionado antes
                            rx.match(
                                #Sigue/lee la variabre ind_grafico que cambia el metodo cambiar_grafico ejecutado antes
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

                                #Texto cuando no se da ningun match
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
                #Condicional para no visualizar el boton de descargan en la mezcla de indicadores
                rx.cond(
                    ~ Programa.ind_mezcla,
                    #Creamos un boton por cada archivo para descargar
                    rx.foreach(
                        datos,
                        lambda item, i: rx.button(
                            f"Descargar {item["name"]}",
                            on_click=Programa.descargar_archivo(i)
                        )
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