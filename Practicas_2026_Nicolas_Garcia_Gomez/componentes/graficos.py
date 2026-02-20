import reflex as rx
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de area
def graf_area(datos: list[dict], bool_esp: bool) -> rx.Component:
    #Condicional que nos permite dibujar un grafico basandose en las especialidades cuando se selecciona el ind por especialidades
    return rx.cond(
        bool_esp,  
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.area_chart(
            #Definimos el area
            rx.recharts.area(
                #Los datos para rellenar el area
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                #Difinimos cuando empieza, cuanto dura y como va a ser la animacion
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
            ),
            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                interval=0,
                #Rota las letras 5 grados hacia abajo
                angle=-5,
                #Alinea la mitad del texto con la marca del eje        
                text_anchor="middle",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(),
            #Indica los valores al pasar el raton
            rx.recharts.graphing_tooltip(),
            #Barra que nos permite seleccionar rango de especialidades
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            data=item["valor"],
            #Marguenes del grafico
            margin={"top": 20, "right": 100, "left": 60, "bottom": 20},
            width=1000,
            height=250,  
            )
        ),
    
        #Creamos el grafico de area
        rx.recharts.area_chart(
            #El contenido del area
            rx.recharts.area(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
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

#Exactamente igual que antes invirtiendo los ejes
def graf_area_vert(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        rx.foreach(
        datos,
        lambda item: rx.recharts.area_chart(
            rx.recharts.area(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            #En el eje x van los numeros
            rx.recharts.x_axis(type_="number"),
            #En el eje y estan las especialidades
            rx.recharts.y_axis(
                data_key="especialidad",
                type_="category", 
                interval=0,
                angle=-10,
                text_anchor="end",    
                height=50,
            ),
            rx.recharts.graphing_tooltip(),
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            data=item["valor"],
            margin={"top": 20, "right": 20, "left": 130, "bottom": 20},
            #Permite ponerlo en vertical
            layout="vertical",
            width=1000,
            height=250,  
            )
        ),    
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            rx.recharts.x_axis(type_="number"),
            rx.recharts.y_axis(data_key = "name", type_="category"),
            rx.recharts.graphing_tooltip(),
            data=datos,
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 20, "bottom": 20},
            width=550,
            height=250,
                
        )
    )

#Para crear graficos de barras
def graf_barras(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.bar_chart(
            #El contenido del grafico las barras
            rx.recharts.bar(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                interval=0,
                angle=-10,
                text_anchor="end",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
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
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
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

#Para crear graficos de barras igual que el anterior pero invirtiendo ejes
def graf_barras_vert(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        rx.foreach(
        datos,
        lambda item: rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            #En el eje x van los valores numericos
            rx.recharts.x_axis(type_="number"),
            #En el eje y las especialidades
            rx.recharts.y_axis(
                data_key="especialidad", 
                type_="category",
                interval=0,
                angle=-10,
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
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                fill=Color.ACENTO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            #En el eje x van los valores numericos
            rx.recharts.x_axis(type_="number"),
            #En el eje y van los años
            rx.recharts.y_axis(data_key="name", type_="category"),
            rx.recharts.graphing_tooltip(),
            layout="vertical",
            data=datos,
            width=550,
            height=250,
                
        )
    )

#Para crear graficos de lineas
def graf_lineas(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        #Creo un grafico por archivo en vertical
        rx.foreach(
        datos,
        lambda item: rx.recharts.line_chart(
            #El contenido del grafico las lineas
            rx.recharts.line(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
            ),
            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                interval=0,
                angle=-10,
                text_anchor="end",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            data=item["valor"],
            margin={"top": 20, "right": 20, "left": 100, "bottom": 20},
            width=1000,
            height=250,  
            )
        ),
    
        #Creamos el grafico de lineas
        rx.recharts.line_chart(
            #El contenido del grafico las lineas
            rx.recharts.line(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
            ),
            #Eje x
            rx.recharts.x_axis(data_key="name"),
            #Eje y
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            data=datos,
            width=550,
            height=250,
                
        )
    )

#Exactamente igual pero invirtiendo los ejes
def graf_lineas_vert(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,        
        rx.foreach(
        datos,
        lambda item: rx.recharts.line_chart(
            rx.recharts.line(
                data_key="indicador",
                stroke=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
            ),
            #En el eje x van los valores numericos
            rx.recharts.x_axis(type_="number"),
            #En el eje y las especialidades
            rx.recharts.y_axis(
                data_key="especialidad", 
                type_="category",
                interval=0,
                angle=-10,
                text_anchor="end",    
                height=50,
            ),
            rx.recharts.graphing_tooltip(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.brush(data_key="especialidad", height=30, stroke=Color.ACENTO.value),
            #Pone el grafico vertical
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 100, "bottom": 20},
            data=item["valor"],
            width=1000,
            height=250,  
            )
        ),    
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="valor",
                stroke=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
            ),
            #En el eje x van los valores numericos
            rx.recharts.x_axis(type_="number"),
            #En el eje y van los años
            rx.recharts.y_axis(data_key="name", type_="category"),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            #Pone el grafico en vertical
            layout="vertical",
            margin={"top": 20, "right": 20, "left": 20, "bottom": 20},
            data=datos,
            width=550,
            height=250,
                
        )
    )

#Para crear graficos de dispersion
def graf_dispersion(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        rx.foreach(
        datos,
        lambda item: rx.recharts.scatter_chart(
            #El contenido del grafico los puntos
            rx.recharts.scatter(
                data=item["valor"], 
                fill=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
            #Eje x
            rx.recharts.x_axis(
                data_key="especialidad", 
                type_="category",
                #Ponemos un dominio de 100 años
                domain=[2000, 2100],
                #Si algun dato pasa del dominio no apareceera
                allow_data_out_of_boundary=True,
                interval=0,
                angle=-10,
                text_anchor="end",    
                height=50,
            ),
            #Eje y
            rx.recharts.y_axis(data_key="indicador", type_="number"),
            rx.recharts.graphing_tooltip(),
            #Cuadricula del fondo 
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            margin={"top": 20, "right": 20, "left": 60, "bottom": 20},
            width=1000,
            height=250,  
            )
        ),
    
        rx.recharts.scatter_chart(
            #El contenido del grafico
            rx.recharts.scatter(
                data=datos, 
                fill=Color.SECUNDARIO.value,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            ),
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

#Para crear graficos de tarta
def graf_pie(datos: list[dict]) -> rx.Component:
    return rx.recharts.pie_chart(
        #Iteramos sobre los años para crear un anillo por cada año
        rx.foreach(
            datos,
            lambda item, i: rx.recharts.pie(
                data=item["valor"],
                data_key="indicador",
                name_key="especialidad",
                #Alternamos colores usando el indice para variar la estetica
                fill=rx.cond(
                    i % 2 == 0, 
                    Color.OSCURO.value, 
                    Color.ACENTO.value
                ),
                #El anillo interior (i=0) empieza en 0% y llega a 30%
                inner_radius=f"{i * 25}%", 
                #El siguiente se va expandiendo hacia afuera
                outer_radius=f"{(i + 1) * 20}%",
                padding_angle=5,
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out"
            )
        ),
        rx.recharts.graphing_tooltip(),
        width=750,
        height=750,
    )

#Para crear graficos de funnel
def graf_funnel(datos: list[dict]) -> rx.Component:
    #Creo un grafico por archivo en vertical
    return rx.foreach(
    datos,
    lambda item: rx.recharts.funnel_chart(
        #El contenido del grafico los niveles
        rx.recharts.funnel(
            #Definimos los nombres para las etiquetas
            name_key="especialidad",
            data_key="indicador",
            data=item["valor"],
            animation_begin=200,
            animation_duration=1500,
            animation_easing="ease-out",
            stroke=Color.OSCURO.value
        ),
        rx.recharts.graphing_tooltip(),
        margin={"top": 20, "right": 20, "left": 20, "bottom": 20},
        width=800,
        height=250, 
        )
    )
