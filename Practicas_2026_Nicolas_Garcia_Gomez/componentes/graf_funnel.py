import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de funnel
def graf_funnel(datos: list[dict]) -> rx.Component:
    #Creo un grafico por archivo en vertical
    return rx.foreach(
    datos,
    lambda item: rx.recharts.funnel_chart(
        #El contenido del grafico
        rx.recharts.funnel(
            rx.recharts.label_list(
                position="center",
                data_key="especialidad",
                fill=Color.SECUNDARIO.value,
            ),
            data_key="indicador",
            data=item["valor"],
            animation_begin=200,
            animation_duration=3000,
            animation_easing="ease-in-out",
            stroke=Color.OSCURO.value

        ),
        rx.recharts.graphing_tooltip(),
        margin={"top": 20, "right": 20, "left": 20, "bottom": 20},
        width=800,
        height=250, 
        )
    )