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
            rx.dialog.title(
                "Resultados del Indicador", 
                color = TextoColor.ACENTO.value
            ),
            rx.vstack(
                #El texto de cada indicador
                rx.text(texto),
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
                    width="100%",
                    height=250,
                )
            ),
            #Para cerrar la ventana
            rx.dialog.close(
                rx.button(
                "Cerrar",
                on_click=Programa.cerrar_ventana
                )
            )
        ),
        #Mostar solo cuando se haya hecho un calculo(se selecciona una opcion)
        open=Programa.mostrar_resultado,
    )