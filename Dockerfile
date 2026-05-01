#1. Usamos una imagen oficial de Python ligera
FROM python:3.12-slim

#2. Instalamos herramientas necesarias (Reflex necesita curl y unzip para funcionar)
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

#3. Le decimos a Docker en que carpeta interna vamos a trabajar
WORKDIR /app

#4. Copiamos el archivo de librerias y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#5. Copiamos el resto del codigo fuente al contenedor
COPY . .

#6. Exponemos los puertos del Frontend (3000) y Backend (8000)
EXPOSE 3000
EXPOSE 8000

#7. El comando que arranca la aplicacion de Reflex en modo produccion
CMD ["reflex", "run", "--env", "prod"]