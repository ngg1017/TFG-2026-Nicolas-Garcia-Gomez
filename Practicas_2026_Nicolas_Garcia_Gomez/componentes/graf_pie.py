import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de tarta
def graf_pie(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        #Creo un grafico por archivo
        rx.recharts.pie_chart(
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
            margin={"top": 20, "right": 20, "left": 60, "bottom": 20},
            width=1000,
            height=250,
        ),

        #MODIFICARRRRRRRRRRRRRRRRRRRRRRRRRRRR
        #Creamos el grafico de barras
        rx.recharts.area_chart(
            #El contenido del grafico
            rx.recharts.area(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value
            ),
            #Eje x
            rx.recharts.x_axis(data_key="name"),
            #Eje y
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            data=datos,
            width=550,
            height=250,
                
        )
    )