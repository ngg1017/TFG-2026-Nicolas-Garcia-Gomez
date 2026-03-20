import reflex as rx
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

def tabla(columnas: list[str], datos: list[list]) -> rx.Component:
    #La base de la tabla   
    return rx.table.root(
        #Define la seccion superior(donde van los nombres de las columnas)
        rx.table.header(
            #Creamos una unica fila
            rx.table.row(
                #Recorre la lista de nombres de columnas, por cada nombre, crea una "celda de cabecera"
                rx.foreach(
                    columnas, 
                    lambda col: rx.table.column_header_cell(col)
                ),
                border = "solid",
                border_color = Color.ACENTO.value
            )
        ),
        #Cuerpo de la tabla
        rx.table.body(
            #Recorre la lista principal de los datos cada elemento row representa una fila completa de datos
            rx.foreach(
                datos,
                #Por cada fila encontrada, crea un componente de fila fisica en la tabla
                lambda row: rx.table.row(
                    #Ahora que estamos dentro de una fila, recorremos cada valor individual que hay en esa fila
                    rx.foreach(
                        row.to(list), 
                        lambda cell: rx.table.cell(cell)
                    )
                )
            ),
            border = "solid",
            border_color = Color.ACENTO.value
        ),
        #Le da un aspecto con fondo solido y bordes suaves
        variant="surface",
        size="1",         
        width="100%",
        margin_bottom="1em",
        overflow="hidden"
    )