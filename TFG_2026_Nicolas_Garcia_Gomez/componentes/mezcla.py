import reflex as rx
from Logica.Programa import Programa
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color

def mezcla() -> rx.Component:
    #Tarjeta que contine la seleccion de los indicadores a mezclar
    return rx.card(
        rx.vstack(
            #Componente flexible que se adapta al tamaño
            rx.flex(
                rx.dialog.title(
                "Seleccione Indicadores",
                color = TextoColor.ACENTO.value,
                ),
                spacing="3",
                align="center",
                width="100%"
            ),
            rx.form.root(
                rx.flex(
                    #La barra de seleccion                    
                    rx.select.root(
                        #Boton del desplegable
                        rx.select.trigger(
                            placeholder="Seleccione un indicador",
                            style={
                                "background_color": Color.OSCURO.value,
                                "color": TextoColor.PRIMARIO.value,
                                "borderRadius": "0.75rem",
                            }
                        ),
                        
                        #Lista desplegable
                        rx.select.content(
                            rx.select.group(
                                #Generamos las opciones una a una para poder darles estilo
                                rx.foreach(
                                    [
                                        "Mortalidad Estandarizada", "Reingresos no Programados", "Incidencia de Barotrauma", 
                                        "Posición Semiincorporada con VMI", "Incidencias Úlcera por Presión UPP", 
                                        "Interrupción Diaria de la Sedación", "Prevención Enfermedad Tromboembólica", 
                                        "Mantenimiento de Niveles de Glucemia", "Resucitación Precoz de la Sepsis", 
                                        "Traslado Intrahospitalario", "Tratamiento Empírico Adecuado", 
                                        "Neumonia Asociada a VMI", "Reintubación", "Profilaxis de Úlcera por Estrés con NE", 
                                        "Sedación Adecuada", "Ingresos Urgentes", "Eventos Adversos Durante el Traslado", 
                                        "Nutrición Enteral Precoz", "Sobretransfusión de Hematíes", "TET por Maniobras", 
                                        "Bacteriemia relacionada a CVC"
                                    ],
                                    lambda ind: rx.select.item(
                                        ind, 
                                        value=ind,
                                        #Color del texto de cada opcion
                                        style={
                                            "color": TextoColor.SECUNDARIO.value,
                                            "_hover": {"color": TextoColor.PRIMARIO.value}
                                        }
                                    )
                                )
                            ),
                            #Color de fondo de la ventana desplegable
                            style={"background_color": Color.ACENTO.value}
                        ),
                        name="indicador",
                        required=True,
                    ),
                    #Botones de control
                    rx.button("Añadir", flex="0.5", type="submit"),
                    rx.button("Borrar", flex="0.1", type="reset", on_click=Programa.borrar_seleccion),
                    width="20%",
                    spacing="3",
                ),
                on_submit=Programa.seleccion_ind,
                reset_on_submit=True,
            ),
            #Barra divisoria
            rx.divider(),
            rx.hstack(
                rx.dialog.title(
                    "Añadidos:",
                    style={"font_size": "2.3rem"},
                    color = TextoColor.ACENTO.value
                ),
                #Componente donde van los indicadores añadidos
                rx.badge(
                    #Una flecha hacia la derecha
                    rx.icon(tag="arrow_right"),
                    #Visualizamos cada indicador añadido
                    rx.foreach(
                        Programa.lista_selecc,
                        lambda x: rx.text(
                            f'"{x}"',
                            align="center",
                            margin_bottom = "0px"
                        )
                    ),
                    align_items = "center",
                    variant = "solid",
                    radius = "full",
                ),
                align_items="center"
            ),
            width="100%",
        ),
        width="100%",
        style={"border": f"2px solid {Color.ACENTO.value}"}
    )
