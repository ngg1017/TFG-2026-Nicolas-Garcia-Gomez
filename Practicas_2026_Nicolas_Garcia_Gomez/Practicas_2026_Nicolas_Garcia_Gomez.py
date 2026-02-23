import reflex as rx
import Practicas_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from Practicas_2026_Nicolas_Garcia_Gomez.views.navbar import navbar
from Practicas_2026_Nicolas_Garcia_Gomez.views.cabecera import cabecera
from Practicas_2026_Nicolas_Garcia_Gomez.views.pie import pie
from Practicas_2026_Nicolas_Garcia_Gomez.views.instrucciones import instrucciones
from Practicas_2026_Nicolas_Garcia_Gomez.views.vent_flotante import vent_flotante
from Logica.Programa import Programa
from Logica.State import State

#Colocamos los elementos de la web
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                cabecera(),
                instrucciones(),
                vent_flotante(Programa.texto, Programa.datos_final),
                pie(),
                width = "100%",
                spacing = "9"
            )
        )
    )

#Establecemos los estilos
app = rx.App(
    stylesheets = estilos.HOJAESTILO,
    style = estilos.ESTILO_BASE
)

#Titulo y descripcion de la web
app.add_page(
    #Le añadimos los componentes
    index,
    #Borra cualquier residuo que haya quedado de sesiones anteriores
    on_load=State.loop_monitor_conexion,
    title = "Indicadores de calidad REA",
    description = "Explciar como subir todos los componentes"
)