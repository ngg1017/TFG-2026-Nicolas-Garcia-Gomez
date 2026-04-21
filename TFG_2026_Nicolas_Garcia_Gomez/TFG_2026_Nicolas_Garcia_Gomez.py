import reflex as rx
import TFG_2026_Nicolas_Garcia_Gomez.estilos.estilos as estilos
from TFG_2026_Nicolas_Garcia_Gomez.views.navbar import navbar
from TFG_2026_Nicolas_Garcia_Gomez.views.cabecera import cabecera
from TFG_2026_Nicolas_Garcia_Gomez.views.pie import pie
from TFG_2026_Nicolas_Garcia_Gomez.views.instrucciones import instrucciones
from TFG_2026_Nicolas_Garcia_Gomez.views.vent_flotante import vent_flotante
from TFG_2026_Nicolas_Garcia_Gomez.views.acceso import acceso
from TFG_2026_Nicolas_Garcia_Gomez.views.vistas_bbdd import vistas_bbdd
from Logica.Programa import Programa
from Logica.Usuarios import Usuarios
from Logica.BBDD import BBDD
from Logica.State import State

def vista() -> rx.Component:
    return rx.cond(
        #Consultar la BBDD
        BBDD.viendo_consulta,
        
        #Si es True: Muestra la pantalla de base de datos
        vistas_bbdd(),
        
        #Si es False: Muestra el panel normal
        rx.box(
            navbar(),
            rx.center(
                rx.vstack(
                    cabecera(),
                    instrucciones(),
                    vent_flotante(Programa.texto, Programa.datos_final, Programa.datos_tarta),
                    pie(),
                    width="100%",
                    spacing="9"
                )
            )
        )
    )

#Llamamos a la pagina principal o a la pagina de acceso
def index() -> rx.Component:
    return rx.cond(
        Usuarios.autenticado,
        #Si la variable autenticado es True. Pasa a ver la pagina principal
        vista(), 
        #Si la variable autenticado es False. Se queda en el login
        acceso()
    )

#Se ejecutal al inciar el servidor
State.limpieza_inteligente_csv()
#Establecemos los estilos
app = rx.App(
    stylesheets = estilos.HOJAESTILO,
    style = estilos.ESTILO_BASE
)

#Titulo y descripcion de la web
app.add_page(
    #Le añadimos los componentes
    index,
    #Funcion de perrito guardian se carga al inicio
    on_load=State.loop_monitor_conexion,
    title = "Indicadores de calidad URCCPQ",
    description = "Calculadora Indicadores de calidad URCCPQ"
)