import reflex as rx
import os

#Lee la URL de los secretos del servidor (Docker o HUBU)
#Si no existe esa variable, usa la base de datos local por defecto
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/tfg_bbdd"
)

config = rx.Config(
    app_name="TFG_2026_Nicolas_Garcia_Gomez",
    #Establece la cadena de conexion directa a postgresql local
    db_url=DATABASE_URL,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)