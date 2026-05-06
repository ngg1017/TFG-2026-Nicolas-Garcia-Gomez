import reflex as rx
from Logica.Usuarios import Usuarios
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from TFG_2026_Nicolas_Garcia_Gomez.componentes.renderizar_campo_formulario import renderizar_campo_formulario
from Logica.BBDD import BBDD

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
                                    border_radius="2rem"
                                )
                            ),
                            #Ordena al contenedor que envuelva los elementos en lugar de encogerlos
                            wrap="wrap",
                            spacing="3"
                        )
                    ),
                    background_color=Color.ACENTO.value, margin_bottom="1em"
                ),

                #Barra de busqueda
                rx.hstack(
                    rx.input(
                        placeholder="Buscar por Nº Historia... Ej. 111111",
                        #Conecta lo que escribe el usuario con la variable del backend
                        value=BBDD.termino_busqueda, 
                        on_change=BBDD.set_termino_busqueda,
                        width="300px",
                    ),
                    rx.button(
                        "Buscar Registro",
                        #Dispara la recarga de datos aplicando el filtro
                        on_click=BBDD.cargar_datos_bd
                    ),
                    #Boton de añadir condicionado al rol
                    rx.cond(
                        Usuarios.rol >= 2,
                        rx.button(
                            "＋ Añadir Registro", 
                            on_click=BBDD.abrir_modal
                        )
                    ),
                    margin_bottom="1em",
                    justify="between" 
                ),
                
                #Caja maestra que sincroniza el scroll horizontal de ambas tablas a la vez
                rx.box( 
                    rx.vstack(
                        #Tabla superior que contiene unicamente los nombres de las columnas fijas
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    #Celda para la papelera (Solo rol >= 2)
                                    rx.cond(
                                        Usuarios.rol >= 2, 
                                        rx.fragment(
                                            rx.table.column_header_cell(
                                                "Borrado", 
                                                width="100px", 
                                                min_width="100px", 
                                                max_width="100px", 
                                                text_align="center", 
                                                background_color=Color.PRIMARIO.value
                                            ),
                                            rx.table.column_header_cell(
                                                "Edición", 
                                                width="100px", 
                                                min_width="100px", 
                                                max_width="100px", 
                                                text_align="center", 
                                                background_color=Color.PRIMARIO.value
                                            )
                                        )
                                    ),
                                    #Itera sobre la lista de alias cortos
                                    rx.foreach(
                                        BBDD.cabeceras_display,
                                        lambda alias: rx.table.column_header_cell(
                                            alias, 
                                            white_space="nowrap",
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
                                            #Boton papelera que usa el ID (fila[0])
                                            rx.cond(
                                                Usuarios.rol >= 2,
                                                rx.fragment(
                                                    rx.table.cell(
                                                        rx.button(
                                                            rx.icon(tag="trash"), 
                                                            on_click=BBDD.borrar_paciente(fila[0])
                                                        ),
                                                        width="100px", 
                                                        min_width="100px", 
                                                        max_width="100px", 
                                                        text_align="center",
                                                    ),
                                                    rx.table.cell(
                                                        rx.button(
                                                            rx.icon(tag="pen"), 
                                                            on_click=BBDD.abrir_modal_edicion(fila[0])
                                                        ),
                                                        width="100px", 
                                                        min_width="100px", 
                                                        max_width="100px", 
                                                        text_align="center",
                                                    )
                                                        
                                                )
                                            ),
                                            #Pinta las celdas usando un condicional sobre el indice
                                            rx.foreach(
                                                fila,
                                                lambda celda, indice: rx.cond(
                                                    #Si es > 0 (no es el ID oculto), dibuja la celda normal
                                                    indice > 0, 
                                                    rx.table.cell(
                                                        celda, 
                                                        white_space="nowrap",
                                                        width="150px", 
                                                        min_width="150px", 
                                                        max_width="150px", 
                                                        text_align="center",
                                                    )
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
                            #Frena el scroll para que no contagie a la pantalla principal
                            style={"overscroll_behavior": "contain"}
                        ),
                        #Elimina la separacion entre las dos tablas para simular que son la misma
                        spacing="0" 
                    ),
                    #Propiedades de la caja maestra que permite el deslizamiento lateral
                    width="100%",
                    overflow_x="auto", 
                    class_name="container-fluid border border-red rounded"
                ),

                #Para añadir pacientes
                rx.dialog.root(
                    rx.dialog.content(
                        rx.dialog.title(
                            rx.cond(
                                BBDD.modal_edicion,
                                "Editar Registro",
                                "Añadir Nuevo Registro",
                            ),
                            color=Color.ACENTO.value
                        ),
                        #Area de relleno
                        rx.scroll_area(
                            rx.vstack(
                                #1: Los 3 elementos de arriba (Ancho completo)
                                rx.foreach(
                                    BBDD.formulario_cabecera,
                                    #Usamos una funcion auxiliar para no repetir codigo
                                    lambda campo: renderizar_campo_formulario(campo) 
                                ),
                                rx.divider(margin_y="10px"),
                                
                                #2: El resto en 2 columnas
                                rx.grid(
                                    rx.foreach(
                                        BBDD.formulario_cuerpo,
                                        lambda campo: renderizar_campo_formulario(campo)
                                    ),
                                    columns="2",
                                    #Espacio entre columnas y filas
                                    spacing="4",

                                    width="100%",
                                ),
                                width="100%",
                            ),
                            height="60vh",
                            padding_right="1em",
                        ),
                        #Botonera
                        rx.hstack(
                            rx.button(
                                "Cancelar", 
                                on_click=BBDD.cerrar_modal
                            ),
                            rx.button(
                                rx.cond(
                                    BBDD.modal_edicion,
                                    "Editar Registro",
                                    "Guardar Registro"
                                ),
                                on_click=BBDD.guardar_nuevo_paciente, 
                            ),
                            margin_top="1em", justify="end"
                        )
                    ),
                    open=BBDD.modal_añadir_abierto,
                ),
                
                #Seccion inferior con los botones de control principal
                rx.divider(margin_top="1em"),
                rx.hstack(
                    rx.button(
                        "Cargar para Análisis", 
                        #Ejecuta el puente de conexion con la logica asincrona
                        on_click=BBDD.preparar_analisis,
                        width="18%",
                        size="3",
                    ),
                    rx.button(
                        "Cancelar", 
                        #Cierra el panel sin realizar ninguna exportacion
                        on_click=BBDD.cerrar_consulta, 
                        width="6%",
                        size="3"
                    ),
                    rx.spacer(),
                    #Boton de exportacion (solo para roles 3)
                    rx.cond(
                        Usuarios.rol >= 3,
                        rx.button(
                            rx.icon(tag="download"),
                            on_click=BBDD.preparar_exportacion,
                            background_color="red",
                            width="7%",
                            size="3",
                            style={
                                "_hover": {
                                    "color": TextoColor.SECUNDARIO.value
                                }
                            }
                        )
                    ),
                    width="100%",
                    spacing="4"
                )
            ),
            padding="2em", 
            box_shadow="lg",
            #Dimensiones relativas para asegurar que la interfaz respire bien en cualquier monitor
            width="90vw",
        ),
        min_height="100vh", 
        padding_y="2em",
        background_color=Color.PRIMARIO.value,
    )