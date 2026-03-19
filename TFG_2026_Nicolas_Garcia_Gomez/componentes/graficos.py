import reflex as rx
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

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

#Grafico de area mezclando indicadores
def graf_ar_mezcla(datos: list[dict], indicadores: list[str]) -> rx.Component:
    #Colores para distinguir las areas
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)

    return rx.recharts.area_chart(
        #Generacion de areas
        rx.foreach(
            indicadores,
            lambda item, i: rx.recharts.area(
                data_key=item,
                stroke=colores_var[i],
                fill=colores_var[i],
                #Transparencia para ver las de atras
                fill_opacity=0.2 + (0.2 * i), 
            )
        ),
        #Configuracion de los ejes
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        rx.recharts.graphing_tooltip(),
        rx.recharts.legend(),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        data=datos,
        width="100%",
        height=430, 
        margin={"left": 10} 
    )

def area_sync(datos: list[dict], indicadores: list[str]) -> rx.Component:
    #Colores para distinguir las areas
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)

    return rx.vstack(
        rx.recharts.bar_chart(
            rx.recharts.graphing_tooltip(),
            rx.recharts.bar(data_key=indicadores[0], stroke=colores_var[0], fill=colores_var[0]),
            rx.recharts.bar(data_key=indicadores[1],stroke=colores_var[1],fill=colores_var[1]),
            rx.recharts.bar(data_key=indicadores[2],stroke=colores_var[2],fill=colores_var[2]),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            rx.recharts.legend(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            data=datos,
            sync_id="1",
            width="100%",
            height=200,
        ),
        rx.recharts.composed_chart(
            rx.recharts.bar(data_key=indicadores[0], stroke=colores_var[0], fill=colores_var[0], bar_size=20),
            rx.recharts.area(data_key=indicadores[1], stroke=colores_var[1], fill=colores_var[1]),
            rx.recharts.line(data_key=indicadores[2], type_="monotone", stroke=colores_var[2]),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            rx.recharts.brush(data_key="name", height=30, stroke="#8884d8"),
            rx.recharts.legend(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            data=datos,
            sync_id="1",
            width="100%",
            height=250,
        ),
        width="100%",
    )

def composed(datos: list[dict], indicadores: list[str]) -> rx.Component:
    #Colores para distinguir las areas
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)

    return rx.recharts.composed_chart(
        rx.recharts.area(data_key=indicadores[0], stroke=colores_var[0], fill=colores_var[0]),
        rx.recharts.bar(data_key=indicadores[1], bar_size=20, fill=colores_var[1]),
        rx.recharts.line(data_key=indicadores[2], type_="monotone", stroke=colores_var[2]),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.graphing_tooltip(),
        data=datos,
        height=250,
        width="100%",
    )

def graf_pie_mezcla(datos: list[dict], indicadores: list[str]) -> rx.Component:
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)
    
    return rx.vstack(
        #El grafico de tarta
        rx.recharts.pie_chart(
            #Por cada nombre de indicador en la lista, genera un objeto "Pie"
            rx.foreach(
                indicadores,
                lambda item, i: rx.recharts.pie(
                    #Entra en los datos de los años y aplica a cada "quesito" del anillo el mismo color del indicador actual
                    rx.foreach(
                        datos,
                        lambda entry, j: rx.recharts.cell(fill=colores_var[i])
                    ),
                    data=datos,
                    data_key=item,
                    name=item,
                    #Cada indicador empiece más afuera que el anterior y no se solapen con la siguiente capa.
                    inner_radius=rx.Var.create(f"{(i * 20) + 10}%"),
                    outer_radius=rx.Var.create(f"{(i + 1) * 20 + 5}%"),
                    padding_angle=5,
                    stroke="none",
                )
            ),
            rx.recharts.graphing_tooltip(),
            width=700,
            height=500,
        ),
        
        #Leyenda manual
        rx.flex(
            #Inicia un bucle para dibujar cada etiqueta de la leyenda (cuadrado + texto) basandose en los indicadores activos.
            rx.foreach(
                indicadores,
                lambda item, i: rx.flex(
                    #Cuadrado de color
                    rx.box(
                        width="14px",
                        height="14px",
                        background_color=colores_var[i],
                        border_radius="3px",
                        flex_shrink="0",
                    ),
                    #Texto de la leyenda
                    rx.text(
                        item, 
                        size="2", 
                        weight="medium",
                        style={
                            #Obligamos a que la linea mida lo mismo que el cuadro
                            "line_height": "14px",
                            #Quitamos cualquier margen automatico  
                            "margin": "0",          
                            "padding": "0",
                            "display": "inline-block",
                            #Alineacion clasica de texto
                            "vertical_align": "middle", 
                        }
                    ),
                    spacing="2",
                    style={
                        "display": "flex",
                        #Centrado vertical real de Flex
                        "align_items": "center",    
                        "justify_content": "center",
                        #Contenedor un poco mas alto para dar aire
                        "height": "20px",           
                    }
                )
            ),
            spacing="5",
            justify="center",
            width="100%",
            flex_wrap="wrap",
            padding_top="1em",
            padding_bottom="2em",
        ),
        width="100%",
        align="center",
    )