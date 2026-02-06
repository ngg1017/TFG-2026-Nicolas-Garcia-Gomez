import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color
from Logica.Programa import Programa

#Devulve la ventana flotante
def vent_flotante(texto: str, datos: list[dict]) -> rx.Component:

    #Ventana flotante
    return rx.dialog.root(

        #Contenido de la ventana
        rx.dialog.content(

            #Titulo
            rx.hstack(
                rx.dialog.title(
                texto.split(":")[0],
                weight="bold",
                color = TextoColor.ACENTO.value,
                white_space="nowrap"
                ),
                justify = "center"
            ),

            rx.vstack(
                #El texto de cada indicador
                rx.text(texto.split(":")[1]),
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
                                spacing="2",
                                width="100%",
                            ),
                            style={
                                "border": f"2px solid {Color.ACENTO.value}"
                            }
                        )  
                    ),
                    margin_x = "auto" 
                ),

                #Creamos el grafico de barras
                rx.recharts.bar_chart(

                    #El contenido del grafico
                    rx.recharts.bar(
                        data_key="valor",
                        stroke=Color.SECUNDARIO.value,
                        fill=Color.ACENTO.value
                    ),
                    #Eje x
                    rx.recharts.x_axis(data_key="name"),
                    #Eje y
                    rx.recharts.y_axis(),
                    data=datos,
                    width=550,
                    height=250,
                ),
                width="100%",
                align="center",
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
                margin_x = "auto",
                justify = "center"
            ),
        
            #Para cerrar la ventana
            rx.dialog.close(
                rx.button(
                "Cerrar",
                on_click=Programa.cerrar_ventana,
                margin_top = "10px"
                )
            ),
            #Permite que el ancho crezca segun el contenido
            width="fit-content", 
            max_width="50vw",      
        ),
        #Mostar solo cuando se haya hecho un calculo(se selecciona una opcion)
        open=Programa.mostrar_resultado,
    )