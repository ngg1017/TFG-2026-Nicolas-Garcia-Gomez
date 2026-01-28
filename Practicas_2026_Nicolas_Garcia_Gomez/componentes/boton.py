import reflex as rx
from Logica.State import State

#Para crear botones
def boton_subida(icon: str) -> rx.Component: 
    return rx.upload.root(
        rx.box(
            rx.icon(
                tag="cloud_upload",
                style={
                    "width": "3rem",
                    "height": "3rem",
                    "color": "#2563eb",
                    "marginBottom": "0.75rem",
                },
            ),
            rx.hstack(
                rx.text(
                    f"{icon}",
                    style={"fontWeight": "bold", "color": "#1d4ed8"},
                ),
                " o arrastra el archivo",
                style={"fontSize": "0.875rem", "color": "#4b5563"},
            ),
            rx.text(
                "CSV",
                style={"fontSize": "0.75rem", "color": "#6b7280", "marginTop": "0.25rem"},
            ),
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "1.5rem",
                "textAlign": "center",
            },
        ),
        id="my_upload",
        multiple=True,
        accept={"documentos/pdf": [".csv"]},
        max_files=3,
        disabled=False,
        no_keyboard=True,
        on_drop=[
            State.limpiar(),
            State.handle_upload(rx.upload_files(upload_id="my_upload"))
        ],

        style={
            "maxWidth": "24rem",
            "height": "16rem",
            "borderWidth": "2px",
            "borderStyle": "dashed",
            "borderColor": "#60a5fa",
            "borderRadius": "0.75rem",
            "cursor": "pointer",
            "transitionProperty": "background-color",
            "transitionDuration": "0.2s",
            "transitionTimingFunction": "ease-in-out",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "boxShadow": "0 1px 2px rgba(0, 0, 0, 0.05)",
        },
    )