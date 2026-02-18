import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de barras
def graf_dispersion(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.scatter_chart(
            #El contenido del grafico
            rx.recharts.scatter(data=item["valor"], fill=Color.SECUNDARIO.value),

            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                type_="category", 
                domain=[2000, 2100],
                allow_data_out_of_boundary=True,
                interval=0,
                #Rota las letras 10 grados hacia abajo
                angle=-10,
                #Alinea el final del texto con la marca del eje        
                text_anchor="end",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(data_key="indicador", type_="number"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            margin={"top": 20, "right": 20, "left": 60, "bottom": 20},
            width=1000,
            height=250,  
            )
        ),
    
        #Creamos el grafico de barras
        rx.recharts.scatter_chart(
            #El contenido del grafico
            rx.recharts.scatter(data=datos, fill=Color.SECUNDARIO.value),
            #Eje x
            rx.recharts.x_axis(
                data_key="name", 
                type_="number", 
                domain=[2000, 2100],
                allow_data_out_of_boundary=True,
            ),
            #Eje y
            rx.recharts.y_axis(data_key="valor", type_="number"),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            data=datos,
            width=550,
            height=250,
                
        )
    )