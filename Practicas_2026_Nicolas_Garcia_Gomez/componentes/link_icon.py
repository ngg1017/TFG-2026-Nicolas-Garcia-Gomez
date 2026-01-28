import reflex as rx

#Para crear botones
def link_icon(icon: str, url: str) -> rx.Component:
    return rx.link(                                   #Creamos el link
        f"{icon}",
        class_name = "btn btn-info btn-lg",        #Importamos de Boostrap el boton
        href = url,                                   #El link que abrimos
        is_external = True,                           #Hacemos que se abrea en una ventana nueva
        weight = "bold",                              #Tipo y debajo tamaño
        size = "8"
    )