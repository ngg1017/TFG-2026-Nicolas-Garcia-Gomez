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
                    rx.select(
                        ["Mortalidad Estandarizada", "Reingresos no Programados", "Incidencia de Barotrauma", "Posición Semiincorporada con VMI", 
                         "Incidencias Úlcera por Presión UPP", "Interrupción Diaria de la Sedación", "Prevención Enfermedad Tromboembólica", 
                         "Mantenimiento de Niveles de Glucemia", "Resucitación Precoz de la Sepsis", "Traslado Intrahospitalario", "Tratamiento Empírico Adecuado", 
                         "Neumonia Asociada a VMI", "Reintubación", "Profilaxis de Úlcera por Estrés con NE", "Sedación Adecuada", "Ingresos Urgentes",
                         "Eventos Adversos Durante el Traslado", "Nutrición Enteral Precoz", "Sobretransfusión de Hematíes",
                         "TET por Maniobras"],
                        name="indicador",
                        #Aparece antes de seleccionar nada
                        placeholder="Seleccione un indicador",
                        required=True,
                    ),
                    #Botones de control
                    rx.button("Añadir", flex="0.5", type="submit"),
                    rx.button("Borrar", flex="0.1", type="reset", on_click=Programa.borrar_seleccion),
                    width="20%",
                    spacing="3",
                ),
                on_submit=Programa.seleccion_ind,
                reset_on_submit=True
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
            align_items="left",
            width="100%",
        ),
        width="100%",
        style={"border": f"2px solid {Color.ACENTO.value}"}
    )
