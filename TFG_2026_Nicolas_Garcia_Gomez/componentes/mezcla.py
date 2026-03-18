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
                        ["Mortalidad Estandarizada", "Reingresos no programados", "Incidencia de barotrauma", "Posicion semiincorporada con VMI", "Incidencias úlcera por presión",
                         "Valoración diaria de la interrupción de la sedación", "Prevención de la enfermedad tromboembólica", "Mantenimiento de niveles de glucemia",
                         "Resucitación precoz de la sepsis", "Traslado intrahospitalario", "Tratamiento empírico adecuado en infección", "Neumonia asociada a ventilacion mecanica",
                         "Reintubación", "Profilaxis de la úlcera por estrés en enfermos con NE", "Sedación adecuada", "Ingresos urgentes",
                         "Eventos adversos durante el traslado intrahospitalario", "Nutrición enteral precoz", "Sobretransfusión de concentrados de hematies",
                         "Retirada accidental del tubo endotraqueal"],
                        name="indicador",
                        #Aparece antes de seleccionar nada
                        placeholder="Selecciona un indicador",
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

    

 
