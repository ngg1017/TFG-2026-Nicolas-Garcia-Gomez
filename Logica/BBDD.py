import reflex as rx
import pandas as pd
import unicodedata
from Logica.State import State 
from Logica.Modelo import Modelo
import io
import zipfile

class BBDD(rx.State):
    #Variable que controla si el panel de la tabla es visible o no
    viendo_consulta: bool = False
    #Lista que almacena temporalmente los años que el usuario selecciona
    años_seleccionados: list[str] = []
    
    #Lista principal con los nombres exactos de la base de datos
    cabeceras: list[str] = [
        "num_historia", "fecha_ingreso", "fecha_alta", "reingreso_48", "especialidad_ingreso", "ingreso_urgencia", "fallecimiento", "apache",
        "vmi", "dias_vmi", "barotrauma", "grados_inclinacion", "episodios_nav", "registro_intubaciones", "extubacion_programada", "extubacion_maniobras",
        "sepsis", "shock_septico", "pam_ingreso", "pam_6h", "pam_24h", "diuresis_ingreso", "diuresis_6h", "diuresis_24h", "lactato_ingreso", "lactato_6h", "lactato_24h",
        "tratamiento_adecuado", "cobertura_empirica_completa", "resistencia_antibioticos", "numero_episodios_bacteriemia", "numero_total_dias_cvc",
        "rass", "bis", "rass_objetivo", "bis_objetivo", "ventana_sedacion",
        "fecha_inicio_ne", "omeprazol", "tratamiento_corticoides", "antecedentes_hemorragia_gi", "coagulopatia", "insuficiencia_renal", "insuficiencia_hepatica",
        "upp", "profilaxis_tvp", "tvp", "glucemia", "tratamiento_insulina", "traslado_intrahospitalario", "listado_verificacion", "eventos_adversos_traslado", "actos_transfusionales", "sangrado_activo", "cantidad_transfusion_dia"
    ]

    #Lista secundaria con abreviaturas legibles exclusivamente para la interfaz grafica
    cabeceras_display: list[str] = [
        "Nº Historia", "Fecha Ingreso", "Fecha Alta", "Reingreso 48h", "Especialidad", "Ingreso Urgencia", "Fallecimiento", "APACHE",
        "VMI", "Días VMI", "Barotrauma", "Grados Inclinación", "Episodios NAV", "Registro Intubación", "Extub. Programada", "Extub. Maniobras",
        "Sepsis", "Shock Séptico", "PAM Ingreso", "PAM 6h", "PAM 24h", "Diuresis Ingreso", "Diuresis 6h", "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", "Lactato 24h",
        "Trat. Adecuado", "Cobertura Empírica", "Resist. Antibióticos", "Bacteriemia", "Días CVC",
        "RASS", "BIS", "RASS Objetivo", "BIS Objetivo", "Ventana Sedación",
        "Fecha Inicio NE", "Omeprazol", "Trat. Corticoides", "Hemorragia GI", "Coagulopatía", "Insuf. Renal", "Insuf. Hepática",
        "UPP", "Profilaxis TVP", "TVP", "Glucemia", "Trat. Insulina", "Traslado Intra.", "Listado Verific.", "Eventos Traslado", "Transfusiones", "Sangrado Activo", "Cant. Transfusiones"
    ]

    #Lista terciaria exclusiva para exportar los CSV con los nombres que exige el script de Pandas
    cabeceras_exportacion: list[str] = [
        "Num Historia", "Fecha Ingreso", "Fecha Alta", "Reingreso 48", "Especialidad de ingreso", "Ingreso por Urgencia", "Fallecimiento", "APACHE",
        "VMI", "Dias VMI", "Barotrauma", "Grados Inclinacion", "Episodios NAV", "Registro Intubaciones", "Extubacion Programada", "Extubacion por Maniobras",
        "Sepsis", "Shock Septico", "PAM ingreso", "PAM 6h", "PAM 24h", "Diuresis Ingreso", "Diuresis 6h", "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", "Lactato 24h",
        "Tratamiento adecuado", "Cobertura empirica completa", "Resistencia antibioticos", "Numero Episodios Bacteriemia", "Numero total de días CVC",
        "RASS", "BIS", "RASS objetivo", "BIS objetivo", "Ventana de sedacion",
        "Fecha Inicio NE", "Omeprazol", "Tratamiento Corticoides", "Antecedentes Hemorragia GI", "Coagulopatia", "Insuficiencia Renal", "Insuficiencia Hepatica",
        "UPP", "Profilaxis TVP", "TVP", "Glucemia", "Tratamiento Insulina", "Traslado Intrahospitalario", "Listado de verificacion", "Eventos Adversos Traslado", "Actos Transfusionales", "Sangrado Activo", "Cantidad Transfusion Dia"
    ]

    #Lista exclusiva para ordenar visualmente el formulario de añadir paciente
    orden_formulario: list[str] = [
        "Nº Historia", "Fecha Ingreso", "Reingreso 48h", "Fecha Alta", "Barotrauma", 
        "VMI", "Días VMI", "RASS Objetivo", "RASS", "BIS Objetivo", "BIS", 
        "Episodios NAV", "Registro Intubación", "Extub. Programada", "Ventana Sedación", 
        "Extub. Maniobras", "Grados Inclinación", "UPP", "Profilaxis TVP", "TVP", 
        "Glucemia", "Trat. Insulina", "Sepsis", "Shock Séptico", "Trat. Adecuado", 
        "Cobertura Empírica", "Resist. Antibióticos", "Bacteriemia", "Días CVC", 
        "PAM Ingreso", "PAM 6h", "PAM 24h", "Diuresis Ingreso", "Diuresis 6h", 
        "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", "Lactato 24h", "Traslado Intra.", 
        "Listado Verific.", "Eventos Traslado", "Fallecimiento", "APACHE", 
        "Trat. Corticoides", "Hemorragia GI", "Coagulopatía", "Insuf. Renal", 
        "Insuf. Hepática", "Especialidad", "Ingreso Urgencia", "Fecha Inicio NE", 
        "Omeprazol", "Transfusiones", "Cant. Transfusiones", "Sangrado Activo"
    ]

    #Matriz bidimensional que contiene todos los registros historicos de los pacientes
    datos_mostrados: list[list[str]] = []

    #Variable para almacenar solo los años
    lista_años_bd: list[str] = []

    #Variable que almacena el numero de historia escrito en el buscador web
    termino_busqueda: str = ""

    #Variable para controlar el dialogo de añadir paciente
    modal_añadir_abierto: bool = False
    
    #Diccionario para capturar los datos del nuevo paciente (54 campos)
    nuevo_paciente_dict: dict = {}

    #Variable para controlar el dialogo de edicion
    modal_edicion: bool = False

    #Guarda el ID interno de la base de datos del paciente que estamos editando
    id_paciente_editar: str = ""

    #Lista de control del formulario
    campos_display_fecha: list[str] = ["Fecha Ingreso", "Fecha Alta", "Fecha Inicio NE"]
    
    campos_display_fecha_multiple: list[str] = ["Registro Intubación"]
    
    campos_display_numerico: list[str] = [
        "APACHE", "Días VMI", "Grados Inclinación", "PAM Ingreso", "PAM 6h", "PAM 24h", 
        "Diuresis Ingreso", "Diuresis 6h", "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", 
        "Lactato 24h", "Bacteriemia", "Días CVC", "RASS", "BIS", "RASS Objetivo", "BIS Objetivo", 
        "Ventana Sedación", "Glucemia", "Cant. Transfusiones"
    ]
    
    campos_display_booleano: list[str] = [
        "Reingreso 48h", "Ingreso Urgencia", "Fallecimiento", "VMI", "Barotrauma", "Episodios NAV",
        "Extub. Programada", "Extub. Maniobras", "Sepsis", "Shock Séptico", "Trat. Adecuado", 
        "Cobertura Empírica", "Resist. Antibióticos", "Omeprazol", "Trat. Corticoides", 
        "Hemorragia GI", "Coagulopatía", "Insuf. Renal", "Insuf. Hepática", "UPP", "Profilaxis TVP", 
        "TVP", "Trat. Insulina", "Traslado Intra.", "Listado Verific.", "Eventos Traslado", 
        "Transfusiones", "Sangrado Activo"
    ]

    #Decorador que indica a reflex que esta variable se calcula dinamicamente
    @rx.var
    def años_disponibles(self) -> list[str]:
        return self.lista_años_bd

    #Funcion puente que viaja a PostgreSQL, extrae los pacientes y formatea la pantalla
    def cargar_datos_bd(self):
        #Abre una sesion de comunicacion segura con la base de datos
        with rx.session() as session:
            #Carga el directorio completo de pacientes en la memoria de Python (No satura RAM)
            pacientes_db = session.exec(Modelo.select()).all()
            
            matriz_formateada = []
            años_temporales = set()
            pacientes_filtrados = []
            
            #1. Lee la fecha de todos para no romper los botones exportadores
            for p in pacientes_db:
                if p.fecha_ingreso and p.fecha_ingreso != "---":
                    año = str(p.fecha_ingreso).split("/")[-1]
                    años_temporales.add(año)
            
            #2. Decide que pacientes van a la pantalla
            #Limpia espacios en blanco del buscador para evitar errores
            busqueda_limpia = self.termino_busqueda.strip().upper()
            
            if busqueda_limpia == "":
                #Si el buscador esta vacio, muestra unicamente el primer paciente de la base de datos
                if len(pacientes_db) > 0:
                    pacientes_filtrados = [pacientes_db[0]] if pacientes_db else []
            else:
                #Si hay texto, busca todos los ingresos asociados a ese numero de historia
                pacientes_filtrados = [p for p in pacientes_db if p.num_historia and p.num_historia.upper() == busqueda_limpia]
                if pacientes_filtrados == []:
                    return rx.toast(f"El numero de historia {self.termino_busqueda} buscado no existe.")
            
            #3. Prepara las 54 columnas solo de los pacientes filtrados
            for p in pacientes_filtrados:
                #Insertamos el id como primer elemento(lo usamos al borrar)
                fila = [str(p.id)]
                for attr in self.cabeceras:
                    valor = getattr(p, attr)
                    fila.append(str(valor) if valor is not None else "---")
                matriz_formateada.append(fila)
            
            #Inyecta los datos a la pantalla
            self.datos_mostrados = matriz_formateada
            self.lista_años_bd = sorted(list(años_temporales), reverse=True)

    #Funcion que gestiona la logica de marcado y desmarcado de los botones de años
    def toggle_año(self, año: str):
        #Verifica si el año pulsado ya se encontraba previamente en la lista
        if año in self.años_seleccionados:
            #Reasigna la lista completa excluyendo el año para forzar la actualizacion visual
            self.años_seleccionados = [a for a in self.años_seleccionados if a != año]

        #Ejecuta el bloque secundario en caso de que el año no estuviera seleccionado
        else:
            #Comprueba que no se haya superado el limite de seguridad de diez archivos
            if len(self.años_seleccionados) < 10:
                #Reasigna la lista añadiendo el nuevo año mediante suma de listas
                self.años_seleccionados = self.años_seleccionados + [año]
            #Bloque que se ejecuta si el usuario intenta superar el limite establecido
            else:
                return rx.toast("Has alcanzado el máximo de 10 años")
    
    #Funcion puente que prepara la interfaz antes del calculo 
    def preparar_analisis(self):
        #Corte de seguridad
        if len(self.años_seleccionados) == 0:
            return rx.toast("Seleccione al menos un año")
            
        #1. Cierra la ventana visual
        self.viendo_consulta = False
        self.termino_busqueda=""
        
        #2. Devuelve una "cadena de ordenes" directas a la interfaz web.
        #Reflex las ejecutara en este orden exacto.
        return [
            #Enciende la barra en el estado principal
            State.set_barra(True),
            #Baja la pantalla          
            rx.scroll_to("zona_de_carga"),
            #Lanza la extraccion de datos  
            BBDD.enviar_a_analisis          
        ]

    #Funcion asincrona responsable de exportar los datos desde PostgreSQL directamente a la RAM
    async def enviar_a_analisis(self):
        estado_principal = await self.get_state(State)
        archivos_creados = 0

        with rx.session() as session:
            todos_pacientes = session.exec(Modelo.select()).all()

            for año in self.años_seleccionados:
                datos_filtrados = []
                
                #Busca los pacientes que coincidan con el año actual
                for p in todos_pacientes:
                    if p.fecha_ingreso and str(p.fecha_ingreso).endswith(año):
                        #Formatea la fila ignorando el num_historia
                        fila = [str(getattr(p, attr)) if getattr(p, attr) is not None else "" for attr in self.cabeceras[1:]]
                        datos_filtrados.append(fila)

                if len(datos_filtrados) == 0:
                    continue

                #Genera el DataFrame a partir de la lista
                df = pd.DataFrame(datos_filtrados, columns=self.cabeceras_exportacion[1:])
                nombre_ficticio = f"BBDD_Historico_{año}.csv"

                #Gestor de memoria de DataFrames en RAM
                while len(estado_principal._dataframes_memoria) >= 10:
                    estado_principal._dataframes_memoria.pop(0)
                    nombre_a_borrar = estado_principal.nombres_archivos.pop(0)
                    estado_principal.nombres_archivos_eliminados.append(nombre_a_borrar)

                #Guardamos el df directo en la RAM
                estado_principal._dataframes_memoria.append(df)
                estado_principal.nombres_archivos.append(nombre_ficticio)
                archivos_creados += 1

        estado_principal.cargados += archivos_creados
        
        #Registro auditoria
        await self.registrar_log_bbdd("ANALISIS_DATOS", f"Análisis en RAM de los años: {self.años_seleccionados}")
        self.años_seleccionados = [] 
        
        #Apaga la barra al terminar
        estado_principal.barra = False
        return rx.toast(f"Registros de {archivos_creados} años cargados listos para análisis.")
    
    #Funcion de borrado
    async def borrar_paciente(self, id_paciente: str):
        with rx.session() as session:
            #Buscamos al paciente por su ID primario
            paciente = session.get(Modelo, int(id_paciente))

            if paciente:
                #Guardamos el num_historia para borrar la busqueda
                numero_historia = paciente.num_historia

                session.delete(paciente)
                session.commit()

                #Registro auditoria
                await self.registrar_log_bbdd("BORRAR_REGISTRO", f"Se eliminó el Nº Historia: {numero_historia}")
                
                #Le pedimos a la base de datos que busque si queda alguna fila con ese mismo numero
                quedan_registros = session.exec(
                    Modelo.select().where(Modelo.num_historia == numero_historia)
                ).first()
                
                #Limpiamos espacios y forzamos mayusculas en ambos textos para compararlos
                termino_limpio = self.termino_busqueda.strip().upper()
                historia_limpia = str(numero_historia).strip().upper()

                if not quedan_registros and termino_limpio == historia_limpia:
                    self.termino_busqueda = ""

                #Recargamos la tabla para que desaparezca visualmente
                self.cargar_datos_bd()
                return rx.toast(f"Registro {paciente.num_historia} eliminado correctamente")

    def abrir_modal(self):
        #Aseguramos que estamos en modo Añadir
        self.modal_edicion = False
        self.id_paciente_editar = ""

        #Inicializamos con los nombres display para que coincidan con la vista web
        self.nuevo_paciente_dict = {attr: "" for attr in self.cabeceras_display}
        self.modal_añadir_abierto = True

    def cerrar_modal(self):
        self.modal_añadir_abierto = False
        self.modal_edicion = False

    def actualizar_campo_nuevo(self, campo: str, valor: str):
        #Hacemos una copia exacta del diccionario actual
        temp_dict = self.nuevo_paciente_dict.copy()
        #Le inyectamos el nuevo valor
        temp_dict[campo] = valor
        #Machacamos la variable original. Esto avisa a Reflex de que hay datos nuevos
        self.nuevo_paciente_dict = temp_dict

    async def guardar_nuevo_paciente(self):
        #1. Validacion de Nº Historia
        n_historia_raw = str(self.nuevo_paciente_dict.get("Nº Historia", "")).strip()
        if n_historia_raw == "":
            return rx.toast("Error: El Nº de Historia es obligatorio")
        try:
            #Si tiene letras o decimales fallara
            self.nuevo_paciente_dict["Nº Historia"] = int(n_historia_raw)
        except ValueError:
            return rx.toast("Error: El Nº de Historia debe ser un número entero (sin letras ni puntos)")

        #2. Validacion de Fechas Simples
        for campo in self.campos_display_fecha:
            valor = str(self.nuevo_paciente_dict.get(campo, "")).strip()
            if valor != "":
                try:
                    #Intentamos convertir la fecha. Si es 345/12/2026, esto lanzara un error.
                    pd.to_datetime(valor, format="%d/%m/%Y", errors="raise")
                except Exception:
                    return rx.toast(f"Error: La fecha en '{campo}' no es válida o no existe (ej. día 345).")

        #3. Validacion de Campos Numericos 
        for campo in self.campos_display_numerico:
            valor = str(self.nuevo_paciente_dict.get(campo, "")).strip()
            if valor != "":
                valor_corregido = valor.replace(",", ".")
                try:
                    num = float(valor_corregido)
                    if num > 999:
                        return rx.toast(f"Error: El valor en '{campo}' parece demasiado alto. El máximo admitido es 999")
                    
                    self.nuevo_paciente_dict[campo] = num 
                except ValueError:
                    return rx.toast(f"Error: La columna '{campo}' solo admite números.")

        #4. Validacion de Fechas
        f_ingreso_str = self.nuevo_paciente_dict.get("Fecha Ingreso", "").strip()
        if f_ingreso_str == "":
            return rx.toast("Error: La Fecha de Ingreso es obligatoria")
        
        f_alta_str = self.nuevo_paciente_dict.get("Fecha Alta", "").strip()
        if f_alta_str == "":
            return rx.toast("Error: La Fecha de Alta es obligatoria")
        
        f_ne_str = self.nuevo_paciente_dict.get("Fecha Inicio NE", "").strip()

        if f_ingreso_str and f_alta_str:
            try:
                #Convertimos temporalmente para comparar
                f_ingreso = pd.to_datetime(f_ingreso_str, format="%d/%m/%Y")
                f_alta = pd.to_datetime(f_alta_str, format="%d/%m/%Y")
                f_ne = pd.to_datetime(f_ne_str, format="%d/%m/%Y")

                #El paciente no puede salir antes de entrar
                if f_alta < f_ingreso:
                    return rx.toast("Error Lógico: La Fecha de Alta no puede ser anterior a la de Ingreso.")
                
                #El paciente tiene que tener NE antes de salir
                if f_alta < f_ne:
                    return rx.toast("Error Lógico: La Fecha de inicio de NE no puede ser posterior a la de Alta.")
                
                #El paciente tiene que tener NE antes de salir
                if f_ne < f_ingreso:
                    return rx.toast("Error Lógico: La Fecha de inicio de NE no puede ser anterior a la de Ingreso.")

            except Exception:
                # Si falla la conversión aquí, los otros validadores de fecha ya avisarán
                pass
        
        #5. Validacion reintubaciones
        valor_intubacion = str(self.nuevo_paciente_dict.get("Registro Intubación", "")).strip()

        if valor_intubacion != "" and valor_intubacion != "None":
            #1. El separador debe ser ';'
            if "," in valor_intubacion or "y" in valor_intubacion.lower() or "-" in valor_intubacion:
                return rx.toast("Error: Use ';' para separar fechas.")

            #2. Validamos cada fecha del listado
            for f in valor_intubacion.split(";"):
                fecha = f.strip()
                if fecha:
                    try:
                        #Si no existe en el calendario dara error
                        pd.to_datetime(fecha, format="%d/%m/%Y", errors="raise")
                    except:
                        return rx.toast(f"Error: La fecha '{fecha}' no es válida.")
                    
        with rx.session() as session:
            datos_limpios = {}
            traductor = dict(zip(self.cabeceras_display, self.cabeceras))
            
            for clave_display, valor in self.nuevo_paciente_dict.items():
                clave_db = traductor[clave_display]
                valor_str = str(valor).strip() if valor is not None else ""
                
                #Conversion a tipos seguros
                if valor_str == "":
                    datos_limpios[clave_db] = None
                elif valor_str == "True":
                    datos_limpios[clave_db] = True
                elif valor_str == "False":
                    datos_limpios[clave_db] = False
                elif clave_display in self.campos_display_numerico or clave_display in self.campos_display_fecha or clave_display in self.campos_display_fecha_multiple:
                    #Los numeros y fechas se guardan tal cual para no romperlos
                    datos_limpios[clave_db] = valor_str
                else:
                    #Descompone las letras y elimina las tildes
                    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", valor_str) if unicodedata.category(c) != "Mn")
                    #Pone la primera letra de cada palabra en mayuscula (.title())
                    datos_limpios[clave_db] = sin_tildes.title().strip()

            if self.modal_edicion:
                #Modo edicion: Buscamos el paciente existente
                paciente_existente = session.get(Modelo, int(self.id_paciente_editar))
                
                if paciente_existente:
                    historia_previa = paciente_existente.num_historia
                    
                    #Machacamos sus atributos antiguos con los nuevos
                    for clave, valor in datos_limpios.items():
                        setattr(paciente_existente, clave, valor)
                    
                    session.add(paciente_existente)
                    session.commit()
                    
                    #Registro auditoria
                    await self.registrar_log_bbdd("EDITAR_REGISTRO", f"Nº Historia editado: {datos_limpios.get('num_historia')}")
                    mensaje_toast = "Registro editado con éxito"

                    #Le pedimos a la base de datos que busque si queda alguna fila con ese mismo numero
                    quedan_registros = session.exec(
                        Modelo.select().where(Modelo.num_historia == historia_previa)
                    ).first()
                    
                    #Limpiamos espacios y forzamos mayusculas en ambos textos para compararlos
                    termino_limpio = self.termino_busqueda.strip().upper()
                    historia_limpia = str(historia_previa).strip().upper()

                    if not quedan_registros and termino_limpio == historia_limpia:
                        self.termino_busqueda=""

                else:
                    return rx.toast("Error crítico: El Registro a editar ya no existe.")
            
            else:
                #Modo añadir: Creamos uno nuevo desde cero
                nuevo = Modelo(**datos_limpios)
                session.add(nuevo)
                session.commit()
                
                #Registro auditoria
                await self.registrar_log_bbdd("NUEVO_REGISTRO", f"Nº Historia creado: {datos_limpios.get('num_historia')}")
                mensaje_toast = "Nuevo registro registrado con éxito"
        
        #Cerramos el modal y reseteamos el modo edicion por seguridad
        self.modal_añadir_abierto = False
        self.modal_edicion = False
        self.id_paciente_editar = ""
        
        #Recargamos la tabla para que se vean los cambios al instante
        self.cargar_datos_bd()
        return rx.toast(mensaje_toast)
    
    #Funcion puente que prepara la interfaz antes de descargar los CSV
    def preparar_exportacion(self):
        #Corte de seguridad
        if len(self.años_seleccionados) == 0:
            return rx.toast("Seleccione al menos un año")
            
        #1. Cierra la ventana visual
        self.viendo_consulta = False
        self.termino_busqueda=""
        
        #2. Devuelve una "cadena de ordenes" directas a la interfaz web.
        #Reflex las ejecutara en este orden exacto.
        return [
            #Enciende la barra en el estado principal
            State.set_barra(True),
            #Baja la pantalla          
            rx.scroll_to("zona_de_carga"),
            #Lanza la extraccion de datos  
            BBDD.exportar_para_pendrive          
        ]
    
    #Funcion para exportar los CSV aninimizados
    async def exportar_para_pendrive(self):
        estado_principal = await self.get_state(State)

        with rx.session() as session:
            todos_pacientes = session.exec(Modelo.select()).all()

            #Creamos un ZIP virtual en la memoria RAM
            zip_buffer = io.BytesIO()

            #Abrimos el ZIP para empezar a meterle los CSV
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                archivos_creados = 0

                for año in self.años_seleccionados:
                    datos_anonimos = []
                
                    for p in todos_pacientes:
                        if p.fecha_ingreso and str(p.fecha_ingreso).endswith(año):
                            #Creamos la fila excluyendo el num_historia (indice 0 de las cabeceras)
                            fila = [str(getattr(p, attr)) if getattr(p, attr) is not None else "" for attr in self.cabeceras[1:]]
                            datos_anonimos.append(fila)

                    if datos_anonimos:
                        #Creamos las cabeceras de exportacion sin el "Num Historia"
                        cabeceras_sin_id = self.cabeceras_exportacion[1:]
                        
                        df = pd.DataFrame(datos_anonimos, columns=cabeceras_sin_id)
                        
                        #Usamos un buffer de memoria para no dejar archivos temporales en el servidor
                        csv_data = df.to_csv(index=False, sep=",", encoding="latin1").encode("latin1")

                        #Metemos el CSV como un archivo dentro del ZIP
                        zip_file.writestr(f"URCCPQ_Anonimo_{año}.csv", csv_data)
                        archivos_creados += 1

            if archivos_creados == 0:
                estado_principal.barra = False
                yield rx.toast("No hay datos para los años seleccionados.")
                return

            #Rebobinamos el archivo virtual para leerlo desde el principio
            zip_buffer.seek(0)
            #Disparamos la descarga del ZIP completo 
            yield rx.download(
                data=zip_buffer.getvalue(),
                filename="Exportacion_Pendrive_BBDD.zip"
            )

        await self.registrar_log_bbdd("EXPORTAR_PENDRIVE", f"Años extraídos: {self.años_seleccionados}")
        estado_principal.barra=False
        self.años_seleccionados = []
        yield rx.toast("Descargas anónimas realizadas correctamente. (Carpeta 'Descargas')")
        return

    #Sistema de auditoria
    async def registrar_log_bbdd(self, accion: str, detalles: str = ""):
        from Logica.Usuarios import Usuarios
        from Logica.Modelo import Auditoria
        
        #Le preguntamos al estado de Usuarios quien esta iniciado en la sesion
        estado_usuario = await self.get_state(Usuarios)
        correo_medico = estado_usuario.email

        with rx.session() as session:
            log = Auditoria(
                usuario_final=correo_medico,
                accion=accion,
                detalles=detalles
            )
            session.add(log)
            session.commit()
    
    def abrir_modal_edicion(self, id_paciente: str):
        #Entramos en modo edicion y guardamos a quien editamos
        self.modal_edicion = True
        self.id_paciente_editar = id_paciente
        
        with rx.session() as session:
            #Buscamos al paciente en la BBDD
            paciente = session.get(Modelo, int(id_paciente))
            
            if paciente:
                self.nuevo_paciente_dict = {}
                #Cruzamos los nombres de la base de datos con los nombres visuales
                for display_name, db_name in zip(self.cabeceras_display, self.cabeceras):
                    valor = getattr(paciente, db_name)
                    #Lo pasamos a string para que se vea bien en los inputs y selects
                    self.nuevo_paciente_dict[display_name] = str(valor) if valor is not None else ""
            else:
                return rx.toast("Error: No se ha encontrado el registro")

        self.modal_añadir_abierto = True
    
    #Metodos que cambia el estado booleano para desplegar la ventana
    def abrir_consulta(self):
        #Lanza la consulta a la base de datos justo antes de abrir el panel
        self.cargar_datos_bd()
        self.viendo_consulta = True

    def cerrar_consulta(self):
        self.viendo_consulta = False
        self.años_seleccionados = []
        self.termino_busqueda = ""
    
    def set_termino_busqueda(self, valor: str):
        self.termino_busqueda = valor