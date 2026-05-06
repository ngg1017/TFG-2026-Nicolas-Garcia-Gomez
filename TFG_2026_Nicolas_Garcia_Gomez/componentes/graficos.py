import reflex as rx
from Logica.Programa import Programa
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

#Para crear graficos lineal
def graf_lineal(datos: list[dict], bool_esp: bool) -> rx.Component:
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
                    custom_attrs={"tooltipType": "none"},     
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
                    type_="linear",
                    active_dot=False           
                ),

                rx.recharts.line(
                    data_key=item+"_tendencia",
                    name="Tendencia",     
                    stroke="white",  
                    active_dot=False,
                    dot=False,
                    type_="monotone"                
                ),

                #El contenido lo ponemos como linea
                rx.recharts.line(
                    data_key=item+"_valor",
                    name="Valor Indicador",
                    fill=Color.ACENTO.value,
                    stroke_width=3,
                    #Quita los puntitos de cada año para que quede limpia 
                    active_dot=False,
                    dot=False,
                    type_="monotone" 
                ),

                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Eje y
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=["auto", "auto"]),
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
                    type_="linear",
                    active_dot=False
                ),

                rx.recharts.line(
                    data_key="tendencia",
                    name="Tendencia",     
                    stroke="white",  
                    active_dot=False,
                    dot=False,
                    type_="monotone"                  
                ),

                #El contenido lo ponemos como linea
                rx.recharts.line(
                    data_key="valor",
                    name="Valor Indicador",
                    fill=Color.ACENTO.value,
                    stroke_width=3,
                    #Quita los puntitos de cada año para que quede limpia 
                    active_dot=False,
                    dot=False,
                    type_="monotone"  
                ),

                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Eje y
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=["auto", "auto"]),
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
                    type_="linear",
                    active_dot=False            
                ),

                rx.recharts.line(
                    data_key=item+"_tendencia", 
                    name="Tendencia",    
                    stroke="white",
                    #Quita los puntitos de cada año para que quede limpia             
                    active_dot=False,
                    dot=False,
                    type_="monotone"                  
                ),

                #El contenido del grafico las barras
                rx.recharts.bar(
                    name="Valor Indicador",
                    data_key=item+"_valor",
                    fill=Color.ACENTO.value,
                    active_dot=False,
                    dot=False,
                    radius=[4, 4, 0, 0] 
                ),

                rx.recharts.x_axis(data_key="name"),
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=["auto", "auto"]),
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
                    type_="linear",
                    active_dot=False            
                ),

                #La tendencia
                rx.recharts.line(
                    data_key="tendencia", 
                    name="Tendencia",    
                    stroke="white",
                    #Quita los puntitos de cada año para que quede limpia             
                    active_dot=False,
                    dot=False,
                    type_="monotone"                  
                ),

                #Los valores en forma de barras
                rx.recharts.bar(
                    name="Valor Indicador",
                    data_key="valor",
                    fill=Color.ACENTO.value,
                    active_dot=False,
                    dot=False,
                    radius=[4, 4, 0, 0]  
                ),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                #Eje x
                rx.recharts.x_axis(data_key="name"),
                #Para darle un poco de aire al grafico por arriba
                rx.recharts.y_axis(domain=["auto", "auto"]),
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
                active_dot=False
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
            rx.recharts.bar(data_key=indicadores[0], stroke=colores_var[0], fill=colores_var[0], radius=[4, 4, 0, 0]),
            rx.recharts.bar(data_key=indicadores[1],stroke=colores_var[1],fill=colores_var[1], radius=[4, 4, 0, 0]),
            rx.recharts.bar(data_key=indicadores[2],stroke=colores_var[2],fill=colores_var[2], radius=[4, 4, 0, 0]),
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
            rx.recharts.bar(data_key=indicadores[0], stroke=colores_var[0], fill=colores_var[0], bar_size=20, radius=[4, 4, 0, 0]),
            rx.recharts.area(data_key=indicadores[1], stroke=colores_var[1], fill=colores_var[1], active_dot=False),
            rx.recharts.line(data_key=indicadores[2], type_="monotone", stroke=colores_var[2], active_dot=False),
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

def graf_barras_mezcla(datos: list[dict], indicadores: list[str]) -> rx.Component:
    #Colores para distinguir las barras
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)

    return rx.recharts.bar_chart(
        #Generacion de barras dinamica
        rx.foreach(
            indicadores,
            lambda item, i: rx.recharts.bar(
                data_key=item,
                fill=colores_var[i],
                #Redondea un poco las esquinas superiores de las barras
                radius=[4, 4, 0, 0] 
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

def graf_lineas_mezcla(datos: list[dict], indicadores: list[str]) -> rx.Component:
    #Colores para distinguir las lineas
    colores = ["#e40707", "#8884d8", "#82ca9d"]
    colores_var = rx.Var.create(colores)

    return rx.recharts.line_chart(
        #Generacion de lineas dinamica
        rx.foreach(
            indicadores,
            lambda item, i: rx.recharts.line(
                data_key=item,
                stroke=colores_var[i],
                #Suaviza un poco los angulos      
                type_="monotone",  
                active_dot=False         
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

