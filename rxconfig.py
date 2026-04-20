import reflex as rx

config = rx.Config(
    app_name="TFG_2026_Nicolas_Garcia_Gomez",
    #Establece la cadena de conexion directa a postgresql local
    db_url="postgresql://postgres:postgres@localhost:5432/tfg_bbdd",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)