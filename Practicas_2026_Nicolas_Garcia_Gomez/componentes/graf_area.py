import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de barras
def graf_area(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.area_chart(
            #El contenido del grafico
            rx.recharts.area(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value
            ),
            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                interval=0,
                #Rota las letras 10 grados hacia abajo
                angle=-5,
                #Alinea el final del texto con la marca del eje        
                text_anchor="middle",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            data=item["valor"],
            margin={"top": 20, "right": 20, "left": 60, "bottom": 20},
            width=1000,
            height=250,  
            )
        ),
    
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