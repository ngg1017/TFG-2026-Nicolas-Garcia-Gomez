import reflex as rx
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from Logica.Programa import Programa

#Creamos el menu de seleccion
def seleccion(icon: str) -> rx.Component:

    #Componente que controla si esta abierto o cerrado
    return rx.drawer.root(

        #Al hacer click dispara la apertura del Drawer
        rx.drawer.trigger(
            rx.button(icon, size="2", font_size="13px"),
            on_click=Programa.manejo_drawer(True)
        ),
        #Es la capa oscura que cubre el resto de la pagina cuando el Drawer se abre
        rx.drawer.overlay(),
        rx.drawer.portal(

            #El contenedor real del panel que se desliza desde la izquierda
            rx.drawer.content(
                rx.vstack(

                    #Boton que cierra el Drawer
                    rx.drawer.close(rx.box(rx.button(
                        "Cerrar",
                        on_click=Programa.manejo_drawer(False)))),

                    #Inicia el componente de menú desplegable lo uso en lugar de rx.select para evitar conflictos de capas dentro del Drawer
                    rx.menu.root(

                        #Abre el menu desplegable
                        rx.menu.trigger(
                            rx.button(
                                "Seleccionar Indicador",
                                variant="surface",
                                width="100%",
                            )
                        ),

                        #Define el contenedor de la lista de opciones
                        rx.menu.content(

                            #Opciones del menu
                            rx.menu.item("Mortalidad Estandarizada", on_click=Programa.mortalidad_estandarizada(ocultar = False)),
                            rx.menu.item("Reingresos no programados", on_click=Programa.reingresos_no_programados(ocultar = False)),
                            rx.menu.item("Incidencia de barotrauma", on_click=Programa.incidencia_de_barotrauma(ocultar = False)),
                            rx.menu.item("Posición semiincorporada con VMI", on_click=Programa.posicion_semiincorporada_VMI(ocultar = False)),
                            rx.menu.item("Incidencias úlcera por presión", on_click=Programa.incidencia_ulceras_presion(ocultar = False)),
                            rx.menu.item(
                                "Valoración diaria de la interrupción de la sedación", 
                                on_click=Programa.valoracion_interrupcion_sedacion(ocultar = False)
                                ),
                            rx.menu.item(
                                "Prevención de la enfermedad tromboembólica", 
                                on_click=Programa.prevencion_enfermedad_tromboembolica(ocultar = False)
                                ),
                            rx.menu.item(
                                "Mantenimiento de niveles de glucemia", 
                                on_click=Programa.mantenimiento_niveles_glucemia(ocultar = False)
                                ),
                            rx.menu.item("Resucitación precoz de la sepsis", on_click=Programa.resucitacion_precoz_sepsis(ocultar = False)),
                            rx.menu.item("Traslado intrahospitalario", on_click=Programa.traslado_intrahospitalario(ocultar = False)),
                            rx.menu.item(
                                "Tratamiento empírico adecuado en infección", 
                                on_click=Programa.tratamiento_empirico_infeccion(ocultar = False)
                            ),
                            rx.menu.item("Neumonía asociada a ventilacion mecánica", on_click=Programa.neumonia_asociada_vmi(ocultar = False)),
                            rx.menu.item("Reintubación", on_click=Programa.reintubacion(ocultar = False)),
                            rx.menu.item("Especialidad con mayor ingreso", on_click=Programa.especialidad_ingreso(ocultar = False)),
                            rx.menu.item(
                                "Profilaxis de la úlcera por estrés en enfermos con NE", 
                                on_click=Programa.profilaxis_ulcera_enfermos_NE(ocultar = False)
                            ),
                            rx.menu.item("Sedación adecuada", on_click=Programa.sedacion_adecuada(ocultar = False)),
                            rx.menu.item("Ingresos urgentes", on_click=Programa.ingresos_urgentes(ocultar = False)),
                            rx.menu.item(
                                "Eventos adversos durante el traslado intrahospitalario", 
                                on_click=Programa.adversos_traslado(ocultar = False)
                            ),
                            rx.menu.item("Nutrición enteral precoz", on_click=Programa.ne_precoz(ocultar = False)),
                            rx.menu.item(
                                "Sobretransfusión de concentrados de hematíes", 
                                on_click=Programa.sobretransfusion_hematies(ocultar = False)
                            ),
                            rx.menu.item("Retirada accidental del tubo endotraqueal", on_click=Programa.retirada_accidental(ocultar = False)),
                            rx.menu.item("Mezcla de indicadores", on_click=Programa.mezcla),
                            rx.menu.item("Resumen Indicadores", on_click=Programa.tabla_resumen),

                            #Aseguramos que el menu flote por encima de todo
                            z_index="500", 
                            background_color=Color.ACENTO.value,
                            color=TextoColor.SECUNDARIO.value,
                        ),
                    ),
                    width="100%",
                ),
                #Difinimos el estilo del panel
                width="20em",
                background_color=Color.PRIMARIO.value,
                padding="2em",
            )
        ),
        #Indica que el panel se abre desde la izquierda de la pantalla
        direction="left",
        #Cuando le clicamos se cierre
        open=Programa.drawer_abierto
    )