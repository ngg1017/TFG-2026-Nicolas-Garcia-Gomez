import reflex as rx
from Logica.Usuarios import Usuarios
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor

#Vista principal, actua como un "controlador de trafico" mostrando una de las 3 
def acceso() -> rx.Component:
    return rx.cond(
        #1. Si el admin ha iniciado sesion en el controlador: Panel Admin
        Usuarios.viendo_gestion,
        vista_gestion_usuarios(),
        rx.cond(
            #2. Si el usuario pulso en "Olvido su contraseña": Pantalla Recuperacion
            Usuarios.viendo_recuperacion,
            cambio_contraseña(),
            
            #3. Por defecto (Flujo normal): Pantalla de Login
            rx.center(
                rx.card(
                    rx.vstack(
                        rx.heading("Acceso - URCCPQ", size="6", align="center"),
                        rx.text("Introduzca sus credenciales para acceder al sistema.", align="center", color="gray"),
                        
                        #Formulario de acceso
                        rx.input(
                            placeholder="Correo electrónico",
                            on_change=Usuarios.actualizar_email,
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            #Oculta los caracteres por seguridad
                            type="password", 
                            on_change=Usuarios.actualizar_password,
                            width="100%"
                        ),
                        
                        #Mensaje de error: Solo se renderiza si la variable no esta vacia
                        rx.cond(
                            Usuarios.mensaje_error != "",
                            rx.text(Usuarios.mensaje_error, color="red", size="2")
                        ),
                        
                        rx.button(
                            "Iniciar Sesión",
                            on_click=Usuarios.iniciar_sesion,
                            width="100%",
                            size="3"
                        ),
                        rx.link(
                            "¿Ha olvidado su contraseña?",
                            color="gray",
                            size="2",
                            on_click=Usuarios.abrir_recuperacion
                        ),
                        
                        #Acesso administrativo
                        rx.divider(),
                        rx.text("Acceso Administrativo", size="2", weight="bold"),
                        rx.hstack(
                            rx.input(
                                placeholder="Email Admin",
                                on_change=Usuarios.set_email_admin_confirmacion,
                                value=Usuarios.email_admin_confirmacion
                            ),
                            rx.input(
                                placeholder="Clave Admin", 
                                type="password", 
                                on_change=Usuarios.set_clave_admin_confirmacion,
                                value=Usuarios.clave_admin_confirmacion
                            ),
                            rx.button("Gestionar", on_click=Usuarios.abrir_gestion, variant="soft"),
                            width="100%"
                        ),
                        spacing="4",
                    ),
                    padding="2em",
                    box_shadow="lg",
                    #Ancho fijo para mantener las proporciones visuales
                    width="400px" 
                ),
                #min_height garantiza que el fondo ocupe al menos la pantalla completa, pero permite crecer si la pantalla es muy pequeña.
                min_height="100vh", 
                background_color=Color.PRIMARIO.value
            )
        )
    )

#Vista de administracion
def vista_gestion_usuarios() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Gestión de Accesos URCCPQ", size="6"),
                rx.text("Panel exclusivo para administración.", color="gray", margin_bottom="1em"),
                
                #Creacion de usuarios
                rx.card(
                    rx.hstack(
                        rx.input(placeholder="Nuevo Email", value=Usuarios.nuevo_email, on_change=Usuarios.set_nuevo_email),
                        rx.input(placeholder="Contraseña", value=Usuarios.nueva_password, on_change=Usuarios.set_nueva_password),
                        
                        #Selector: Permite control total sobre el diseño
                        rx.select.root(
                            #1. Trigger: El boton fisico que el usuario ve y clica
                            rx.select.trigger(
                                placeholder="Rol",
                                background_color=Color.OSCURO.value,
                                color="gray"
                            ),
                            #2. Content: El menu desplegable que se abre
                            rx.select.content(
                                rx.foreach(
                                    ["1", "2", "3"],
                                    lambda rol: rx.select.item(
                                        rol, 
                                        value=rol,
                                        #Estilos interactivos aplicados a cada opcion
                                        style={
                                            "color": TextoColor.SECUNDARIO.value,
                                            "_hover": {"color": TextoColor.PRIMARIO.value}
                                        }
                                    )
                                ),
                                style={"background_color": Color.ACENTO.value}
                            ),
                            #3. Logica de enlace de datos
                            value=Usuarios.nuevo_rol,
                            on_change=Usuarios.set_nuevo_rol,
                        ),
                        rx.button(
                            "Añadir", 
                            on_click=Usuarios.añadir_usuario, 
                            style={"bg": Color.ACENTO.value}
                        ),
                        align_items="center",
                    ),
                    background_color=Color.OSCURO.value,
                    margin_bottom="1em"
                ),
                
                #Visualizacion y eliminacion (tabla)
                rx.box( 
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Email"),
                                rx.table.column_header_cell("Contraseña"),
                                rx.table.column_header_cell("Rol"),
                                rx.table.column_header_cell("Acciones"),
                            )
                        ),
                        rx.table.body(
                            #Bucle renderizador: Genera una fila HTML por cada elemento en la lista
                            rx.foreach(
                                Usuarios.lista_usuarios_tabla,
                                lambda usr: rx.table.row(
                                    rx.table.cell(usr[0]), 
                                    rx.table.cell(usr[1]), 
                                    rx.table.cell(usr[2]), 
                                    rx.table.cell(
                                        rx.button(
                                            rx.icon(tag="trash"),
                                            size="1",
                                            on_click=Usuarios.eliminar_usuario(usr[0]) 
                                        )
                                    )
                                )
                            )
                        ),
                        width="100%"
                    ),
                    #Evitan que la pantalla "explote" si hay muchos usuarios
                    max_height="40vh", 
                    overflow_y="auto", 
                    width="100%",
                    class_name = "container-fluid border border-red rounded"
                ),
                
                #Cierre
                rx.divider(margin_top="2em"),
                rx.button("Cerrar Panel de Gestión", on_click=Usuarios.cerrar_gestion, width="100%")
            ),
            padding="2em",
            box_shadow="lg",
            width="650px",
            #Limita la tarjeta entera 
            max_height="90vh",
            #Scroll de emergencia general 
            overflow_y="auto"  
        ),
        min_height="100vh", 
        background_color=Color.PRIMARIO.value
    )

#Recuperacion
def cambio_contraseña() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Cambio de Contraseña", size="6", align="center"),
                rx.text("Introduzca sus credenciales para poder cambiar su contraseña.", align="center", color="gray"),
                
                rx.input(
                    placeholder="Introduzca su correo electrónico",
                    on_change=Usuarios.set_email_antiguo,
                    width="100%"
                ),
                rx.input(
                    placeholder="Contraseña Nueva",
                    type="password",
                    on_change=Usuarios.set_contraseña_nueva,
                    width="100%"
                ),
                rx.input(
                    placeholder="Repita la Contraseña",
                    type="password",
                    on_change=Usuarios.set_contraseña_nueva2,
                    width="100%"
                ),
                
                rx.cond(
                    Usuarios.mensaje_error != "",
                    rx.text(Usuarios.mensaje_error, color="red", size="2")
                ),
                
                #Boton de accion
                rx.button(
                    "Aceptar",
                    on_click=Usuarios.cambiar_contraseña,
                    width="100%",
                    size="3"
                ),
                rx.divider(),
                rx.button(
                    "Cancelar", 
                    on_click=Usuarios.cerrar_recuperacion,
                    width="25%", 
                    size="3"
                ),
                spacing="4",
            ),
            padding="2em",
            box_shadow="lg",
            width="400px" 
        ),
        min_height="100vh", 
        background_color=Color.PRIMARIO.value
    )
    