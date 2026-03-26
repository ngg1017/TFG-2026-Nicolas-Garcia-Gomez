import reflex as rx
from Logica.Programa import Programa
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos de area
def graf_area(datos: list[dict], bool_esp: bool) -> rx.Component:
    #Condicional que nos permite dibujar un grafico por especialidad cuando se selecciona el ind por especialidades
    return rx.cond(
        bool_esp,  
        #Creo un grafico por cada especialidad
        rx.foreach(
        Programa.nombres_especialidades,
        lambda item, i: rx.vstack(
            #El titulo
            rx.text(
                item,
                size="5"
            ),
            #Introducimos los textos de las tendencias y la r2 y por cada indicador
            rx.text(
                f"{Programa.texto_tendencia[i]}\n\n{Programa.texto_r2[i]}",
                white_space="pre-wrap"
            ),
            rx.recharts.composed_chart(
                #Pilar Invisible (Fondo)
                rx.recharts.area(
                    data_key=item+"_base_invisible",
                    #Activamos el apilado
                    stack_id=item,            
                    stroke="none",
                    #100% transparente
                    fill="transparent",      
                    fill_opacity=0,
                    #Quitamos que se puedan seleccionar los puntos con el raton
                    active_dot=False,
                    type_="linear",
                    #Elimina esta seccion del tooltype
                    custom_attrs={"tooltipType": "none"}          
                ),
                
                #Banda de error(Apoyada exactamente sobre la base)
                rx.recharts.area(
                    data_key=item+"_grosor_banda",
                    name="Amplitud de Variabilidad",
                    #Se apoya en el ID 1
                    stack_id=item,            
                    stroke="none",
                    fill="red",
                    fill_opacity=0.2,
                    type_="linear"           
                ),

                #El contenido lo ponemos como linea
                rx.recharts.line(
                    data_key=item+"_valor",
                    name="Valor Indicador",
                    fill=Color.ACENTO.value,
                    stroke_width=3,
                    #Quita los puntitos de cada año para que quede limpia 
                    dot=False 
                ),

                rx.recharts.line(
                    data_key=item+"_tendencia",
                    name="Tendencia",     
                    stroke="white",  
                    dot=False                 
                ),
                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Eje y
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=[0, "auto"]),
                rx.recharts.graphing_tooltip(),
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
                data=datos,
                width=1000,
                height=250,  
                ),
                #Introducimos una sola vez el texto del error
                rx.cond(
                    i+1 == Programa.nombres_especialidades.length(),
                    rx.text(
                        Programa.texto_error[i]
                    )
                ),
                align="center",
                margin_bottom="3em",
            )
        ),
    
        #Creamos el grafico compuesto
        rx.vstack(
            #Introducimos los textos de las tendencias, la r2 y el error
            rx.text(
                f"{Programa.texto_tendencia[0]}\n\n{Programa.texto_r2[0]}\n\n{Programa.texto_error[0]}",
                white_space="pre-wrap"
            ),
            rx.recharts.composed_chart(
                #Pilar Invisible (Fondo)
                rx.recharts.area(
                    data_key="base_invisible",
                    #Activamos el apilado
                    stack_id="1",            
                    stroke="none",
                    #100% transparente
                    fill="transparent",      
                    fill_opacity=0,
                    #Quitamos que se puedan seleccionar los puntos con el raton
                    active_dot=False,
                    type_="linear",
                    #Elimina esta seccion del tooltype
                    custom_attrs={"tooltipType": "none"}          
                ),
                
                #Banda de error(Apoyada exactamente sobre la base)
                rx.recharts.area(
                    data_key="grosor_banda",
                    name="Amplitud de Variabilidad",
                    #Se apoya en el ID 1
                    stack_id="1",            
                    stroke="none",
                    fill="red",
                    fill_opacity=0.2,
                    type_="linear"           
                ),

                #El contenido lo ponemos como linea
                rx.recharts.line(
                    data_key="valor",
                    name="Valor Indicador",
                    fill=Color.ACENTO.value,
                    stroke_width=3,
                    #Quita los puntitos de cada año para que quede limpia 
                    dot=False 
                ),

                rx.recharts.line(
                    data_key="tendencia",
                    name="Tendencia",     
                    stroke="white",  
                    dot=False                 
                ),
                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Eje y
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=[0, "auto"]),
                rx.recharts.graphing_tooltip(),
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
                data=datos,
                width=1000,
                height=250,    
            ),
            align="center",
            margin_bottom="3em",
            margin_top="3em"
        )
    )

#Para crear graficos de barras
def graf_barras(datos: list[dict], bool_esp: bool) -> rx.Component:
    return rx.cond(
        bool_esp,
        #Creo un grafico por cada especialidad
        rx.foreach(
        Programa.nombres_especialidades,
        lambda item, i: rx.vstack(
            rx.text(
                #El titulo
                item,
                size="5"
            ),
            #Introducimos los textos de las tendencias y la r2 y por cada indicador
            rx.text(
                f"{Programa.texto_tendencia[i]}\n\n{Programa.texto_r2[i]}",
                white_space="pre-wrap"
            ),
            rx.recharts.composed_chart(
                #El contenido del grafico las barras
                rx.recharts.bar(
                    #Metemos el ErrorBar 
                    rx.recharts.error_bar(
                        data_key=item+"_error", 
                        name = "Amplitud de Variabilidad",
                        stroke="red"   
                    ),
                    name="Valor Indicador",
                    data_key=item+"_valor",
                    fill=Color.ACENTO.value,
                ),
                rx.recharts.line(
                    data_key=item+"_tendencia", 
                    name="Tendencia",    
                    stroke="white",
                    #Quita los puntitos de cada año para que quede limpia             
                    dot=False                 
                ),
                rx.recharts.x_axis(data_key="name"),
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=[0, "auto"]),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                #Animaciones
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
                data=datos,
                width=1000,
                height=250,  
                ),
                #Introducimos una sola vez el texto del error
                rx.cond(
                    i+1 == Programa.nombres_especialidades.length(),
                    rx.text(
                        Programa.texto_error[i]
                    )
                ),
                align="center",
                margin_bottom="3em"
            )
        ),
    
        #Creamos el grafico de barras compuesto
        rx.vstack(
            #Introducimos los textos de las tendencias, la r2 y el error
            rx.text(
                f"{Programa.texto_tendencia[0]}\n\n{Programa.texto_r2[0]}\n\n{Programa.texto_error[0]}",
                white_space="pre-wrap"
            ),
            rx.recharts.composed_chart(
                rx.recharts.bar(
                    #Metemos el ErrorBar 
                    rx.recharts.error_bar(
                        data_key="error", 
                        name = "Amplitud de Variabilidad",
                        stroke="red"   
                    ),
                    name="Valor Indicador",
                    data_key="valor",
                    fill=Color.ACENTO.value,
                ),

                rx.recharts.line(
                    data_key="tendencia", 
                    name="Tendencia",    
                    stroke="white",
                    #Quita los puntitos de cada año para que quede limpia             
                    dot=False                 
                ),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=[0, "auto"]),
                rx.recharts.graphing_tooltip(),
                #Animaciones
                animation_begin=200,
                animation_duration=1500,
                animation_easing="ease-out",
                data=datos,
                width=1000,
                height=250,
            ),
            align="center",
            margin_bottom="3em",
            margin_top="3em"
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
                #Multiplicamos por "i" para saber donde empieza el anillo
                inner_radius=f"{i * (100 / datos.length())}%", 
                #Le restamos 2 al final para dejar siempre el margen transparente de separacion
                outer_radius=f"{((i + 1) * (100 / datos.length())) - 2}%",
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