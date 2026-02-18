import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de barras
def graf_lineas_vert(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.line_chart(
            #El contenido del grafico
            rx.recharts.line(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value
            ),
            #Eje x
            rx.recharts.x_axis(type_="number"),
            #Eje y
            rx.recharts.y_axis(
                data_key="especialidad", 
                type_="category",
                interval=0,
                #Rota las letras 10 grados hacia abajo
                angle=-10,
                #Alinea el final del texto con la marca del eje        
                text_anchor="end",    
                height=50,
            ),
            rx.recharts.graphing_tooltip(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 100, "bottom": 20},
            data=item["valor"],
            width=1000,
            height=250,  
            )
        ),
    
        #Creamos el grafico de barras
        rx.recharts.line_chart(
            #El contenido del grafico
            rx.recharts.line(
                data_key="valor",
                stroke=Color.SECUNDARIO.value
            ),
            #Eje x
            rx.recharts.x_axis(type_="number"),
            #Eje y
            rx.recharts.y_axis(data_key="name", type_="category"),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 20, "bottom": 20},
            data=datos,
            width=550,
            height=250,
                
        )
    )