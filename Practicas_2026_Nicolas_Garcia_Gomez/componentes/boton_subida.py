import reflex as rx
from Logica.State import State
from Practicas_2026_Nicolas_Garcia_Gomez.estilos.colores import TextoColor, Color

#Para crear botones
def boton_subida(icon: str) -> rx.Component:
    #Nos permite crear el area de subida
    return rx.upload.root(
        rx.box(

            #La nube
            rx.icon(
                tag="cloud_upload",
                style={
                    "width": "3rem",
                    "height": "3rem",
                    "color": TextoColor.ACENTO.value,
                    "marginBottom": "0.75rem",
                },
            ),
            rx.hstack(
                rx.text(
                    f"{icon}",
                    style={"fontWeight": "bold", "color": TextoColor.ACENTO.value},
                ),
                "o arrastra el archivo",
                style={"fontSize": "0.875rem", "color": TextoColor.TERCIARIO.value},
            ),
            rx.text(
                "CSV",
                style={"fontSize": "0.875rem", "color": TextoColor.ACENTO.value, "marginTop": "0.25rem"},
            ),

            #Estilo de la caja dentro de la subida
            style={
                #Esto permite que alignItems y justifyContent funcione
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "1.5rem",
                "textAlign": "center"
            },
        ),

        #Propiedades del boton
        id="my_upload",
        multiple=True,
        disabled=State.barra,
        no_keyboard=True,
        #Las acciones que se dan al ejecutarse la subida
        on_drop=State.handle_upload(rx.upload_files(upload_id="my_upload")),
        
        #Estilo de la subida
        style={
            #Tamaño
            "maxWidth": "20rem",
            "height": "16rem",
            #Tamaño del borde
            "borderWidth": "3px",
            "borderStyle": "dashed",
            "borderColor": Color.OSCURO.value,
            "borderRadius": "0.75rem",
            #Cursor
            "cursor": "pointer",
            #Propiedades al subir o pasar el raton
            "transitionProperty": "background-color",
            "transitionDuration": "0.2s",
            "transitionTimingFunction": "ease-in-out",
            #Centrar y justificar todos los componentes
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            #Sombra
            "boxShadow": "0 2px 2px rgba(0, 0, 0, 0.05)",
        },
    )