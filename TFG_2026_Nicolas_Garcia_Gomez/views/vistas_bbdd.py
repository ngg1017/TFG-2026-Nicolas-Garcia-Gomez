import reflex as rx
from Logica.BBDD import BBDD
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor

#Funcion principal que dibuja la vista de carga desde la base de datos
def vistas_bbdd() -> rx.Component:
    return rx.center(
        #Tarjeta principal que contiene toda la interfaz grafica
        rx.card(
            rx.vstack(
                rx.heading("Base de Datos Clínicos", size="6"),
                rx.text("Explorador de registros completos. Deslice lateralmente para ver todas las columnas.", color="gray", margin_bottom="1em"),
                
                #Seccion del selector multiple de años
                rx.card(
                    rx.vstack(
                        rx.text("Seleccione los años a procesar (Máx 10):", weight="bold"),
                        
                        #Contenedor flexible que empuja los botones a la linea inferior si no caben en pantalla
                        rx.flex(
                            #Bucle que dibuja un boton por cada año detectado en la base de datos
                            rx.foreach(
                                BBDD.años_disponibles,
                                lambda año: rx.button(
                                    año,
                                    #Dispara la funcion de la logica al hacer clic
                                    on_click=BBDD.toggle_año(año),
                                    
                                    #Evalua en tiempo real si el año esta en la lista para pintarlo de un color u otro
                                    background_color=rx.cond(
                                        BBDD.años_seleccionados.contains(año),
                                        TextoColor.PRIMARIO.value,
                                        Color.OSCURO.value
                                    ),
                                    
                                    #Modifica el color del texto dinamicamente segun la seleccion
                                    color=rx.cond(
                                        BBDD.años_seleccionados.contains(año),
                                        TextoColor.SECUNDARIO.value,
                                        TextoColor.PRIMARIO.value
                                    ),
                                    #Inyecta css puro para el efecto visual al pasar el raton por encima
                                    style= {
                                        "_hover": {
                                            "bg": TextoColor.PRIMARIO.value,
                                            "color": TextoColor.SECUNDARIO.value
                                        }
                                    },
                                    border_radius="2rem", 
                                    cursor="pointer",
                                )
                            ),
                            #Ordena al contenedor que envuelva los elementos en lugar de encogerlos
                            wrap="wrap",
                            spacing="3"
                        )
                    ),
                    background_color=Color.ACENTO.value, margin_bottom="1em"
                ),
                
                #Caja maestra que sincroniza el scroll horizontal de ambas tablas a la vez
                rx.box( 
                    rx.vstack(
                        #Tabla superior que contiene unicamente los nombres de las columnas fijas
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    #Itera sobre la lista de alias cortos para mejorar la legibilidad
                                    rx.foreach(
                                        BBDD.cabeceras_display,
                                        lambda alias: rx.table.column_header_cell(
                                            alias, 
                                            white_space="nowrap",
                                            #Fuerza medidas exactas y restrictivas para alinear esta celda con la de abajo
                                            width="150px", 
                                            min_width="150px",
                                            max_width="150px",
                                            text_align="center",
                                            background_color=Color.PRIMARIO.value,
                                        )
                                    )
                                )
                            ),
                            width="max-content",
                            #Bloquea el diseño elastico del navegador para respetar los pixeles definidos
                            style={"table_layout": "fixed"}
                        ),

                        #Tabla inferior encargada de gestionar los pacientes y el scroll vertical
                        rx.box( 
                            rx.table.root(
                                rx.table.body(
                                    #Doble bucle para recorrer primero la lista de pacientes y luego sus valores
                                    rx.foreach(
                                        BBDD.datos_mostrados,
                                        lambda fila: rx.table.row(
                                            rx.foreach(
                                                fila,
                                                lambda celda: rx.table.cell(
                                                    celda, 
                                                    white_space="nowrap",
                                                    #Aplica las mismas medidas matematicas que la cabecera para evitar descuadres
                                                    width="150px",
                                                    min_width="150px",
                                                    max_width="150px",
                                                    text_align="center",
                                                )
                                            )
                                        )
                                    )
                                ),
                                width="max-content",
                                style={"table_layout": "fixed"}
                            ),
                            #Limita la altura maxima y activa el scroll vertical exclusivo para los datos
                            max_height="45vh", 
                            overflow_y="auto", 
                            #Desactiva el scroll horizontal secundario para que lo gestione la caja maestra
                            overflow_x="hidden", 
                        ),
                        #Elimina la separacion entre las dos tablas para simular que son la misma
                        spacing="0" 
                    ),
                    #Propiedades de la caja maestra que permite el deslizamiento lateral
                    width="100%",
                    overflow_x="auto", 
                    class_name="container-fluid border border-red rounded"
                ),
                
                #Seccion inferior con los botones de control principal
                rx.divider(margin_top="1em"),
                rx.hstack(
                    rx.button(
                        "Cargar para Análisis", 
                        #Ejecuta el puente de conexion con la logica asincrona
                        on_click=BBDD.enviar_a_analisis,
                        width="100%",
                        size="3",
                    ),
                    rx.button(
                        "Cancelar", 
                        #Cierra el panel sin realizar ninguna exportacion
                        on_click=BBDD.cerrar_consulta, 
                        width="30%",
                        size="3"
                    ),
                    width="20%",
                    spacing="4"
                )
            ),
            padding="2em", 
            box_shadow="lg",
            #Dimensiones relativas para asegurar que la interfaz respire bien en cualquier monitor
            width="90vw",
            max_height="90vh"
        ),
        min_height="100vh", 
        background_color=Color.PRIMARIO.value
    )