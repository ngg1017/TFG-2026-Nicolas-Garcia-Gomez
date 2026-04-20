import reflex as rx
import pandas as pd
import tempfile
import os
from Logica.State import State 
from Logica.Modelo import Modelo

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

    #Matriz bidimensional que contiene todos los registros historicos de los pacientes
    datos_mostrados: list[list[str]] = []

    #Variable para almacenar solo los años
    lista_años_bd: list[str] = []

    #Variable que almacena el numero de historia escrito en el buscador web
    termino_busqueda: str = ""

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
                    pacientes_filtrados = [pacientes_db[0]]
            else:
                #Si hay texto, busca todos los ingresos asociados a ese numero de historia
                pacientes_filtrados = [p for p in pacientes_db if p.num_historia and p.num_historia.upper() == busqueda_limpia]
            
            #3. Prepara las 54 columnas solo de los pacientes filtrados
            for p in pacientes_filtrados:
                fila = []
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

    #Funcion asincrona responsable de exportar los datos desde PostgreSQL al analizador
    async def enviar_a_analisis(self):
        estado_principal = await self.get_state(State)
        archivos_creados = 0

        #Abre sesion directa con la BBDD para no saturar la RAM de la web
        with rx.session() as session:
            #Extrae la base de datos completa de fondo
            todos_pacientes = session.exec(Modelo.select()).all()

            for año in self.años_seleccionados:
                datos_filtrados = []
                
                #Busca los pacientes que coincidan con el año actual
                for p in todos_pacientes:
                    if p.fecha_ingreso and str(p.fecha_ingreso).endswith(año):
                        #Formatea la fila con los atributos exactos pero reemplazando nulos por vacio para el CSV
                        fila = [str(getattr(p, attr)) if getattr(p, attr) is not None else "" for attr in self.cabeceras]
                        datos_filtrados.append(fila)

                if len(datos_filtrados) == 0:
                    continue

                #Genera el CSV directamente
                df = pd.DataFrame(datos_filtrados, columns=self.cabeceras_exportacion)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='latin1', newline='') as tmp:
                    df.to_csv(tmp, sep=',', index=False)
                    ruta_tmp = tmp.name

                nombre_ficticio = f"BBDD_Historico_{año}.csv"

                #Gestor de memoria de archivos
                while len(estado_principal.rutas_archivos) >= 10:
                    ruta_a_borrar = estado_principal.rutas_archivos.pop(0)
                    nombre_a_borrar = estado_principal.nombres_archivos.pop(0)
                    estado_principal.nombres_archivos_eliminados.append(nombre_a_borrar)
                    if os.path.exists(ruta_a_borrar):
                        os.remove(ruta_a_borrar)

                estado_principal.rutas_archivos.append(ruta_tmp)
                estado_principal.nombres_archivos.append(nombre_ficticio)
                archivos_creados += 1

        estado_principal.cargados += archivos_creados
        self.años_seleccionados = [] 
        
        #Apaga la barra al terminar
        estado_principal.barra = False
        return rx.toast(f"Registros de {archivos_creados} años cargados.")
    
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