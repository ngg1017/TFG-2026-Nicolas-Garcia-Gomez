import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de tarta
def graf_pie(datos: list[dict]) -> rx.Component:
    #Creo un grafico por archivo
    return rx.recharts.pie_chart(
        #Iteramos sobre los años para crear un anillo por cada año
        rx.foreach(
            datos,
            lambda item, i: rx.recharts.pie(
                data=item["valor"],
                data_key="indicador",
                name_key="especialidad",
                #Alternamos colores o usamos el indice para variar la estetica
                fill=rx.cond(i % 2 == 0, Color.ACENTO.value, Color.SECUNDARIO.value),
                
                #El anillo interior (i=0) empieza en 0% y llega a 30%
                #El siguiente se va expandiendo hacia afuera
                inner_radius=f"{i * 25}%", 
                outer_radius=f"{(i + 1) * 20}%",
                padding_angle=5,
            )
        ),
        rx.recharts.graphing_tooltip(),
        width=750,
        height=750,
    )