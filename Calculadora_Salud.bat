::Oculta los comandos internos del script para que el usuario solo vea los mensajes limpios de texto
@echo off
::Personalizamos la ventana de la terminal (Titulo y texto verde sobre fondo negro)
title Servidor - Calculadora de Salud
color 0A

::cd /d "%~dp0" obliga a que el directorio de trabajo sea la carpeta actual del script.
::Esto evita errores si el programa se ejecuta con permisos de administrador.
cd /d "%~dp0"

echo ========================================================
echo        INICIANDO LA CALCULADORA DE SALUD...
echo ========================================================
echo.

::Comprobamos de forma silenciosa si Python esta instalado en el sistema operativo.
::Si el codigo de error (ERRORLEVEL) es 0, Python existe y saltamos a PYTHON_NATIVO.
::Si no, saltamos a PYTHON_PORTATIL para instalarlo.
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 GOTO PYTHON_NATIVO
GOTO PYTHON_PORTATIL


::RUTA A: El ordenador ya tiene python
:PYTHON_NATIVO
echo [OK] Python nativo detectado en este ordenador.

::Comprobamos si ya existe el entorno virtual de usos anteriores
IF EXIST "entorno_local\Scripts\activate.bat" GOTO ENTORNO_EXISTE

echo [!] Es la primera vez. Creando entorno virtual local (Sandbox)...
python -m venv entorno_local
echo [!] Descargando librerias necesarias (requirements.txt)...
::Activamos el entorno e instalamos las dependencias aisladas del sistema
call entorno_local\Scripts\activate.bat
::Lee el archivo de texto y descarga de Internet automáticamente Reflex, Pandas, y el resto de dependencias.
pip install -r requirements.txt
::Guardamos el comando de ejecucion en una variable
set "COMANDO_REFLEX=reflex run"
GOTO INICIAR_SERVIDOR

:ENTORNO_EXISTE
echo [OK] Entorno virtual listo.
::Activamos el entorno y preparamos el comando
call entorno_local\Scripts\activate.bat
set "COMANDO_REFLEX=reflex run"
GOTO INICIAR_SERVIDOR


::RUTA B: El ordenador no tiene python
:PYTHON_PORTATIL
echo [!] Python NO detectado en el sistema.
echo [!] Preparando motor portatil independiente...

::Comprobamos si ya descargamos el motor portatil anteriormente
IF EXIST "python_portable\python.exe" GOTO PORTATIL_EXISTE

echo [!] Configurando el motor portatil (Esto tomara un par de minutos)...
::Usamos PowerShell para descargar el nucleo de Python oficial en formato ZIP
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.2/python-3.12.2-embed-amd64.zip' -OutFile 'python.zip'"
::Extraemos el contenido en la carpeta python_portable y borramos el ZIP
powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath 'python_portable' -Force"
del python.zip

::Modificamos el archivo de configuracion ._pth para habilitar 'site-packages'.
::Esto nos permitira instalar librerias de terceros (como Reflex o Pandas) en esta version portable.
powershell -Command "$texto = Get-Content 'python_portable\python312._pth'; $texto = $texto -replace '#import site', 'import site'; Set-Content 'python_portable\python312._pth' -Value $texto"

::Descargamos e instalamos el gestor de paquetes PIP
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_portable\get-pip.py'"
"python_portable\python.exe" "python_portable\get-pip.py" >nul
del "python_portable\get-pip.py"

::Usamos el PIP recien instalado para descargar nuestras librerias
"python_portable\python.exe" -m pip install -r requirements.txt
echo [OK] Instalacion portatil completada.

::Guardamos el comando de ejecucion apuntando al motor portatil
set "COMANDO_REFLEX="python_portable\python.exe" -m reflex run"
GOTO INICIAR_SERVIDOR

:PORTATIL_EXISTE
echo [OK] Motor portatil listo.
set "COMANDO_REFLEX="python_portable\python.exe" -m reflex run"
GOTO INICIAR_SERVIDOR


::Arranque final del servidor y el navegador
:INICIAR_SERVIDOR
echo.
echo ========================================================
echo   Compilando aplicacion web. Esto puede tardar un poco...
echo   El navegador se abrira AUTOMATICAMENTE cuando termine.
echo.
echo   Para apagar la calculadora, simplemente cierra esta ventana.
echo ========================================================
echo.

::Le decimos a Reflex que guarde las subidas en la carpeta oculta Temp de Windows
set "REFLEX_UPLOAD_DIR=%TEMP%\reflex_uploads"

::Este subproceso invisible de PowerShell hace 'ping' al puerto 3000 cada segundo. 
::Usamos 'start /B' para que PowerShell corra como un hilo fantasma en el fondo de esta misma ventana.
::Añadimos -NoProfile para que arranque al instante.
::En el instante exacto en que Reflex termina de compilar y abre el puerto,
::el script captura la conexion exitosa, lanza la web en el navegador y se autodestruye.
start /B "" powershell -NoProfile -Command "$i=0; while($i -lt 60){try{$tcp=New-Object System.Net.Sockets.TcpClient('127.0.0.1', 3000);$tcp.Close();Start-Process 'http://localhost:3000';break}catch{Start-Sleep -Seconds 1; $i++}}" >nul 2>&1

::Arrancamos el servidor (usando la version nativa o la portatil segun corresponda)
%COMANDO_REFLEX%

pause