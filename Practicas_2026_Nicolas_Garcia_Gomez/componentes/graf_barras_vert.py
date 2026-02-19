import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de barras
def graf_barras_vert(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.bar_chart(
            #El contenido del grafico
            rx.recharts.bar(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value
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
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 100, "bottom": 20},
            data=item["valor"],
            width=1000,
            height=250,  
            )
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
            rx.recharts.x_axis(type_="number"),
            #Eje y
            rx.recharts.y_axis(data_key="name", type_="category"),
            rx.recharts.graphing_tooltip(),
            layout="vertical",
            data=datos,
            width=550,
            height=250,
                
        )
    )         