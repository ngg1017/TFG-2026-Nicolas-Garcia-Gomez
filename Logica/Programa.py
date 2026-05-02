from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from Logica.PDF import PDF
from .State import State
import reflex as rx
import pandas as pd
import unicodedata
import numpy as np
import asyncio
import re
import io

#Hereda de mi clase State
class Programa(State):
    #Almecen de todos los datos a mostrar
    datos_final: list[dict]
    _csv_final: list[dict] = []
    texto: str

    #Indicadores para mostrar la ventana, el drawer y el indicador por especialidad
    mostrar_resultado: bool
    drawer_abierto: bool
    ind_especi: bool

    #Indicadores para mostrar la tabla resumen
    ind_resumen: bool
    lista_unida: list[list[str], list[list]] = []

    #Indicador para controlar los graficos que se visualizan
    ind_grafico: str

    #Indicador para controlar la mezcla de indicadores
    ind_mezcla: bool
    lista_selecc: list[str]
    datos_mezcla: list[dict]

    #Datos que guardamos solamente para el grafico de tarda de las especialidades
    datos_tarta: list[dict]

    #Lista que guardamos para generar un grafico por especialidad
    nombres_especialidades: list[str]

    #Texto que guardamos para mostrar en los graficos
    texto_tendencia: list[str]
    texto_r2: list[str]
    texto_error: list[str]

    #Variable donde guardaremos todos los datos estadisticos de los indicadores
    _memoria_informe: list[dict] = []

    #Metodo que nos permite encontrar el año del documento
    def encontrar_año(self, nombre: str):
        return re.findall(r"\d{4}", nombre)[0] if re.findall(r"\d{4}", nombre) else "0000"
    
    #Metodo para normalizar las columnas de los dataframes
    def normalizar_frame(self, columna: str, esp_ingreso = False):
        #Colapsa multiples espacios internos en uno solo y borra los de los extremos
        texto_espaciado = " ".join(columna.split())
        #Limpiamos tildes y espacios laterales para ambos casos
        texto_limpio = unicodedata.normalize("NFD", texto_espaciado).encode("ascii", "ignore").decode("utf-8")

        if esp_ingreso:
            #Devuelve formato de especialidades
            return texto_limpio.title()

        #Devuelve formato columnas
        #Un "+" en regex colapsa multiples simbolos raros en un solo "_" a la primera
        return re.sub(r"[^A-Z0-9]+", "_", texto_limpio.upper()).strip("_")
    
    #Metodo para parsear los datos del indicador de ingresoso por especialidad
    def parseo_especialidad(self, datos, resumen = False):
        #Creamos una lista con cada especialidad para crear el esqueleto del diccionario
        lista_especialidades = set()

        #Si los datos vienen del metodo individual se reciben sin el nombre
        for año in datos:
            for especialidad in año["valor"] if resumen == True else año:
                lista_especialidades.add(especialidad["especialidad"].split("_")[0])
                            
        #La guardamos para usarla en los graficos
        self.nombres_especialidades = list(lista_especialidades)

        #Creamos el diccionario con la lista creado anteriormente y lo rellenamos con sus valores
        diccionario_datos = {especialidad: [0.0] * len(datos) for especialidad in lista_especialidades}
        for i, año in enumerate(datos):
            for especialidad in año["valor"] if resumen == True else año:
                diccionario_datos[especialidad["especialidad"].split("_")[0]][i] = especialidad["indicador"]

        #Devolvemos el diccionario relleno
        return diccionario_datos

    #Metodo para parsear los datos aptos para la ventana flotante y los graficos(ordenandolos)
    def parsear_datos(self, resultado_final: list[float], ocultar = False):        
        #Si no estamos en la tabla resumen y son los ingresos por especialidad
        if self.ind_especi == True and ocultar == False:
            
            #Llamamos a la funcion que se encarga de parseas los datos del indicador
            diccionario_datos = self.parseo_especialidad(resultado_final)

            #Creamos el esqueleto de datos_final con los años
            self.datos_final = [{"name": self.encontrar_año(nombre)} for nombre in self.nombres_archivos]

            #Recorremos el diccionario para obtener los datos para cada especialidad
            for especialidad, valores_historicos in diccionario_datos.items():

                #Llamamos a la funcion del calculo para cada especialidad concreta
                y_tendencia, error_tipico, pendiente_tendencia, r2 = self.calculos_estadisticos(self.nombres_archivos, valores_historicos, individual=True)

                #Obtenemos los textos explicativos segun la pendente, la r2 y los guardamos
                texto_tendencia, texto_r2, texto_error = PDF.texto_tendencia_r2(pendiente_tendencia, r2)
                self.texto_tendencia.append(texto_tendencia)
                self.texto_r2.append(texto_r2)
                self.texto_error.append(texto_error)

                #Repartimos los calculos año a año a datos_final
                for i in range(len(self.nombres_archivos)):
                    self.datos_final[i][f"{especialidad}_valor"] = round(valores_historicos[i], 4)
                    self.datos_final[i][f"{especialidad}_tendencia"] = round(y_tendencia[i], 4)
                    self.datos_final[i][f"{especialidad}_base_invisible"] = round((y_tendencia[i] - error_tipico), 4)
                    self.datos_final[i][f"{especialidad}_grosor_banda"] = round((error_tipico*2), 4)
                        
            #Guardamos los datos especificos para el grafico de tarta
            self.datos_tarta = [
                {"name": self.encontrar_año(nombre), "valor": round(valor, 4) if self.ind_especi == False else valor} 
                for nombre, valor in zip(self.nombres_archivos, resultado_final)
            ]

        #Si no estamos en la tabla resumen y es un indicador normal
        elif ocultar == False:
            #Llamamos a la funcion de calculos para obtener la tendencia, el error, la pendiente y r2
            y_tendencia, error_tipico, pendiente_tendencia, r2 = self.calculos_estadisticos(self.nombres_archivos, resultado_final, individual=True)
            
            #Obtenemos los textos explicativos segun la pendente, la r2 y los guardamos
            texto_tendencia, texto_r2, texto_error = PDF.texto_tendencia_r2(pendiente_tendencia, r2)
            self.texto_tendencia = [texto_tendencia]
            self.texto_r2 = [texto_r2]
            self.texto_error = [texto_error]

            self.datos_final = [
                {
                    "name": self.encontrar_año(nombre), 
                    "valor": round(valor, 4), 
                    "tendencia": round(tend,4), 
                    "base_invisible": round((tend - error_tipico),4),
                    "grosor_banda": round((error_tipico * 2),4)
                } 
                for nombre, valor, tend in zip(self.nombres_archivos, resultado_final, y_tendencia)
            ]

        #En el resumen no necesito la tendencia y la r2 ya que hacemos los graficos en matplotlib directamente
        else:
            self.datos_final = [
                {"name": self.encontrar_año(nombre), "valor": round(valor, 4) if self.ind_especi == False else valor} 
                for nombre, valor in zip(self.nombres_archivos, resultado_final)
            ]
        
        #Ordenamos la lista de diccionarios csv_final por años para que se muestren y descarguen por orden
        self.datos_final.sort(key= lambda x: x["name"])
        self._csv_final.sort(key= lambda x: x["name"])

    #Metodo para cerrar la ventana flotante
    def cerrar_ventana(self):
        self.mostrar_resultado = False
        self.ind_especi = False
        self.ind_resumen = False
        self.ind_mezcla = False
        self.ind_grafico = ""
        self.lista_selecc = []
        self.datos_mezcla = []
        self.datos_tarta = []
    
    #Metodo para abrir el drawer
    def manejo_drawer(self, bandera: bool):
        self.drawer_abierto = bandera
    
    #Metodo para limpiar todas las variables necesarias e instanciar la lista de resultados
    def limpieza(self):
        self.manejo_drawer(False)
        self.datos_final = []
        self.texto = ""
        self._csv_final = []
        self.nombres_especialidades = []
        self.texto_tendencia = []
        self.texto_r2 = []
        self.texto_error = []
        resultado = []
        return resultado
    
    #Metodo que hace el proceso final de todos los metodos.
    def final(self, datos: list[float], texto: str, ocultar = False):
        if ocultar == False: 
            self.parsear_datos(datos)
            self.texto = texto
            self.mostrar_resultado = True
            return rx.toast(f"Análisis de los {len(self.nombres_archivos)} documentos completado") if len(self.nombres_archivos) > 1 else rx.toast(f"Análisis del documente completado")
        
        #Si ocultar=True(tabla resumen) solo muestra la tabla resumen
        else: 
            self.texto = texto
            self.parsear_datos(datos, ocultar)
        
    #Metodo que crea el csv que se va a descargar con las columnas y sus transformaciones correspondientes de cada indicador
    def csv_metodo(self,resumen: dict, nombres: list[str], datos: list[pd.DataFrame], nombre_archivo: str):
        #Creamos el resumen (la fila de arriba)
        df_resumen = pd.DataFrame(resumen)

        #Juntamos las columnas de datos para formar la tabla principal
        #axis=1 para pegar las columnas una al lado de la otra
        df_principal = pd.concat(datos, axis=1)

        #Renombramos las columnas para que coincidan EXACTAMENTE con el resumen
        df_principal.columns = nombres

        #Pegamos el resumen arriba y los datos abajo
        df_final_para_doctora = pd.concat([df_resumen, df_principal], ignore_index=True)
        self._csv_final.append({"name": nombre_archivo, "valor": df_final_para_doctora})
    
    #Metodo que se dispara al presionar el boton de descarga y que basicamente hace lo que indica su nombre
    def descargar_archivo(self, indice: int):
        #Obtenemos el dataFrame y su nombre de la lista de diccionarios
        datos = self._csv_final[indice]["valor"]
        nombre = self._csv_final[indice]["name"]

        #Lo convertimos a STRING (formato CSV)
        archivo = datos.to_csv( 
            sep=",",         
            index=False,
            encoding="utf-8-sig"
        )
    
        #Disparamos la descarga con nombre y datos correctos
        return rx.download(
            data=archivo,
            filename=f"{nombre}"
        )
    
    #Metodo para cambiar la variable del grafico
    def cambiar_grafico(self, grafico: str):
        self.ind_grafico = grafico

    #Metodo para la conversion del codigo apache
    def codigo_apache(self, apache: int):
        if pd.isna(apache): return 0
        elif apache <= 4: return 0.04
        elif apache <= 9: return 0.08
        elif apache <= 14: return 0.15
        elif apache <= 19: return 0.25
        elif apache <= 24: return 0.40
        elif apache <= 29: return 0.55
        elif apache <= 34: return 0.75
        else: return 0.85

    def mortalidad_estandarizada(self, ocultar = False):
        resultado = self.limpieza()

        try:
            #Iteramos sobre los archivos temporales en RAM
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                #Hacemos una copia para no alterar la BBDD en RAM
                df = dataframe_memoria.copy()

                #Reemplazo ultrarapido
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})

                #Normalizamos sus columnas
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    #Esto elimina las columnas repetidas quedandose solo con la primera que encuentre
                    df = df.loc[:, ~df.columns.duplicated()]

                if "APACHE" not in df.columns:
                    raise ValueError(f"Falta la columna 'Apache' en {nombre}")
                
                if "FALLECIMIENTO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fallecimiento' en {nombre}")
                
                #Logica de calculo
                fallecimiento = df["FALLECIMIENTO"].fillna(False)
                numero_fallecidos = len(df[fallecimiento == True])

                #Asegura que son numeros (los errores se vuelven NaN)
                apache = pd.to_numeric(df["APACHE"], errors="coerce")
                df["PROBABILIDAD_MORTALIDAD"] = apache.apply(self.codigo_apache)
                suma_mortalidad = df.loc[fallecimiento == True, "PROBABILIDAD_MORTALIDAD"].sum()
                
                valor_final = (numero_fallecidos / suma_mortalidad) if suma_mortalidad != 0 else 0.0
                resultado.append(float(valor_final))

                #Csv que necesita la doctora con los datos filtrados
                data_resumen = {
                    "APACHE": ["RESUMEN GLOBAL mortalidad estandarizada"],
                    "APACHE_TOTAL": [f"Total: {suma_mortalidad}"],
                    "FALLECIMIENTO": [f"Total: {numero_fallecidos}"],
                    "PROBABILIDAD_MORTALIDAD": [f"SMR: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["APACHE","FALLECIMIENTO"], [df["PROBABILIDAD_MORTALIDAD"], fallecimiento],
                    #Busca 4 numeros seguidos (\d{4}) en el nombre y los extrae
                    f"indicador_mortalidad_{self.encontrar_año(nombre)}.csv" 
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        #Metodo que hace todas las operaciones finales para ahorrarnos algo de codigo.
        #Le pasamos la bandera ocultar por si seleccionamos el resumen
        self.final(resultado, "Mortalidad Estandarizada:Es un indicador de resultado que mide la calidad y efectividad " \
        "de un Servicio de Medicina Intensiva (SMI). " \
        "Su propósito es corregir las limitaciones de la 'mortalidad cruda'.", ocultar=ocultar)
        
    def reingresos_no_programados(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})

                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "FECHA_ALTA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha alta' en {nombre}")
                
                if "REINGRESO_48" not in df.columns:
                    raise ValueError(f"Falta la columna 'Reingreso 48' en {nombre}")
                
                #Logica de calculo
                #Conversion a fechas
                df["FECHA_ALTA"] = pd.to_datetime(df["FECHA_ALTA"], format="%d/%m/%Y", errors="coerce")
                reingreso = df["REINGRESO_48"].fillna(False)

                #Contar reingresos
                numero_reingresos = reingreso.sum()

                #Contar altas
                numero_alta = (df["FECHA_ALTA"].notna()).sum()

                valor_final = (numero_reingresos/numero_alta)*100 if numero_alta != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "FECHA_ALTA": ["RESUMEN GLOBAL reingresos no programados"],
                    "REINGRESO_48": [f"Total: {numero_reingresos}"],
                    "NUMERO_ALTAS": [f"Total: {numero_alta}"],
                    "REINGRESOS_NO_PROGRAMADOS": [f"SMI: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["FECHA_ALTA","REINGRESO_48"], [df["FECHA_ALTA"], df["REINGRESO_48"]], 
                    f"indicador_reingresos_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Reingresos no Programados:Es un indicador de resultado que mide la proporción de pacientes que, " \
        "tras haber sido dados de alta de la UCI a una planta de hospitalización, " \
        "deben ser reingresados de forma imprevista en la UCI en un periodo de 48 horas.", ocultar=ocultar)

    def incidencia_de_barotrauma(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})

                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "BAROTRAUMA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Barotrauma' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
                
                #Logica de calculo
                #Conversion a horas
                horas_vmi = pd.to_numeric(df["DIAS_VMI"], errors="coerce")*24

                numero_barotrauma = (df["BAROTRAUMA"].fillna(False) == True).sum()

                #Suma en dias de aquellos que tengan mas de 12 horas
                dias_barotrauma = (horas_vmi[horas_vmi > 12] / 24).sum()

                valor_final = (numero_barotrauma/dias_barotrauma)*1000 if dias_barotrauma != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "BAROTRAUMA": ["RESUMEN GLOBAL incidencia de barotrauma"],
                    "DIAS_VMI": [f"Total: {dias_barotrauma}"],
                    "NUMERO_BAROTRAUMA": [f"Total: {numero_barotrauma}"],
                    "INDICE_BAROTRAUMA": [f"Baro: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["BAROTRAUMA","DIAS_VMI"], [df["BAROTRAUMA"].fillna(False), (horas_vmi/24)], 
                    f"indicador_barotrauma_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")
        
        self.final(resultado, "Incidencia de Barotrauma:Es un indicador de seguridad y proceso que mide la aparición de complicaciones " \
        "pulmonares relacionadas con el daño físico provocado por la ventilación mecánica.", ocultar=ocultar)

    def posicion_semiincorporada_VMI(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "GRADOS_INCLINACION" not in df.columns:
                    raise ValueError(f"Falta la columna 'Grados Inclinacion' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
                
                #Logica de calculo
                dias_vmi = pd.to_numeric(df["DIAS_VMI"], errors="coerce")
                inclinacion = pd.to_numeric(df["GRADOS_INCLINACION"], errors="coerce")

                dias_vmi_totales = dias_vmi[dias_vmi > 0].sum()
                #Inclinacion mayor a 20 y que tengan dias de vmi
                total_inclinacion = dias_vmi[(inclinacion >= 20) & (dias_vmi > 0)].sum()

                valor_final = (total_inclinacion/dias_vmi_totales)*100 if dias_vmi_totales != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "GRADOS_INCLINACION": ["RESUMEN GLOBAL posicion semiincorporada"],
                    "DIAS_VMI": [f"Total: {dias_vmi_totales}"],
                    "NUMERO_INCLINACION": [f"Total: {total_inclinacion}"],
                    "INDICE_POSICION": [f"VMI: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["GRADOS_INCLINACION","DIAS_VMI"], [inclinacion, dias_vmi], 
                    f"indicador_posicion_semiincorporada_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Posición Semiincorporada con VMI:Es un indicador de proceso que mide el porcentaje de pacientes " \
        "con ventilación mecánica invasiva que se mantienen con el cabecero de la cama elevado 20º, con el fin de prevenir " \
        "la neumonía asociada a la ventilación", ocultar=ocultar)
    
    def incidencia_ulceras_presion(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "UPP" not in df.columns:
                    raise ValueError(f"Falta la columna 'UPP' en {nombre}")
            
                #Logica de calculo
                upp = df["UPP"].fillna(False)

                #Pacientes que tengan ulceras por presion
                total_upp = upp[upp == True].sum()
                total_ingresados = len(df)

                valor_final = (total_upp/total_ingresados)*100 if total_ingresados != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "UPP": ["RESUMEN GLOBAL indice UPP"],
                    "TOTAL_UPP": [f"Total: {total_upp}"],
                    "TOTAL_INGRESADOS": [f"Total: {total_ingresados}"],
                    "INDICE_UPP": [f"UPP: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["UPP"], [upp], 
                    f"indicador_upp_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Incidencias Úlcera por Presión UPP:Es un indicador de seguridad que mide el porcentaje " \
        "de pacientes que desarrollan lesiones en la piel o tejidos subyacentes por presión prolongada durante su estancia en " \
        "la UCI, con el objetivo de evaluar la efectividad de las medidas de prevención y cuidados de enfermería", ocultar=ocultar)

    def valoracion_interrupcion_sedacion(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "VENTANA_DE_SEDACION" not in df.columns:
                    raise ValueError(f"Falta la columna 'Ventana de sedacion' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
            
                #Logica de calculo
                int_sedacion = pd.to_numeric(df["VENTANA_DE_SEDACION"], errors="coerce")
                dias_vmi = pd.to_numeric(df["DIAS_VMI"], errors="coerce")

                #Simplemente que tengan sedacion y dias de vmi
                total_sedacion = int_sedacion[(int_sedacion > 0) & (dias_vmi > 0)].sum()

                valor_final = (total_sedacion/dias_vmi.sum())*100 if dias_vmi.sum() != 0 else 0.0
                resultado.append(float(valor_final))

                #Csv que necesita la doctora con los datos filtrados
                data_resumen = {
                    "VENTANA_DE_SEDACION": ["RESUMEN GLOBAL interrupcion sedacion"],
                    "DIAS_VMI": [f"Total: {dias_vmi.sum()}"],
                    "TOTAL_SEDACION": [f"Total: {total_sedacion}"],
                    "INDICE_SEDACION": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["VENTANA_DE_SEDACION", "DIAS_VMI"], [int_sedacion, dias_vmi], 
                    f"indicador_sedacion_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Interrupción Diaria de la Sedación:Es un indicador de proceso que mide el porcentaje " \
        "de días en los que se evalúa y ejecuta la suspensión diaria de la sedación continua en pacientes con ventilación mecánica, " \
        "con el fin de reducir la duración del soporte ventilatorio y la estancia en la UCI. " \
        "Debido a la estructura de la base de datos, " \
        "donde la interrupción de la sedación se registra como una variable dicotómica (Sí/No) por paciente y no de forma diaria, el indicador " \
        "se ha calculado asumiendo que el cumplimiento del protocolo se extiende a la totalidad de los días de ventilación " \
        "mecánica del paciente registrado.", ocultar=ocultar)
    
    def prevencion_enfermedad_tromboembolica(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "PROFILAXIS_TVP" not in df.columns:
                    raise ValueError(f"Falta la columna 'Profilaxis TVP' en {nombre}")
                
                if "TVP" not in df.columns:
                    raise ValueError(f"Falta la columna 'TVP' en {nombre}")
            
                #Logica de calculo
                profilaxis = df["PROFILAXIS_TVP"].fillna(False)
                tvp = df["TVP"].fillna(False)

                #Aquellos que tengas profilaxis y tvp a la vez
                total_tvp = profilaxis[(profilaxis == True) & (tvp == True)].sum()
                total_ingresados = len(df)

                valor_final = (total_tvp/total_ingresados)*100 if total_ingresados != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "PROFILAXIS_TVP": ["RESUMEN GLOBAL enfermedad tromboembolica"],
                    "TVP": [f"Total: {tvp.sum()}"],
                    "TOTAL_PROFILAXIS": [f"Total: {profilaxis.sum()}"],
                    "TOTAL_PROFILAXIS_TVP": [f"Total: {total_tvp}"],
                    "INDICE_TROMBOEMBOLICO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["PROFILAXIS_TVP", "TVP"], [profilaxis, tvp], 
                    f"indicador_tvp_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Prevención Enfermedad Tromboembólica:Es un indicador de proceso que mide el porcentaje de pacientes " \
        "que reciben profilaxis antitrombótica adecuada (farmacológica o mecánica), " \
        "con el fin de evitar complicaciones graves como la trombosis venosa profunda o el tromboembolismo pulmonar.", ocultar=ocultar)

    def mantenimiento_niveles_glucemia(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "GLUCEMIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Glucemia' en {nombre}")
                
                if "TRATAMIENTO_INSULINA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Tratamiento insulina' en {nombre}")
            
                #Logica de calculo
                glucemia = pd.to_numeric(df["GLUCEMIA"], errors="coerce")
                insulina = df["TRATAMIENTO_INSULINA"].fillna(False)

                #Aquellos que tengas insulina y glucemia > 180 a la vez
                total = insulina[(glucemia >= 180) & (insulina == True)].sum()
                total_glucemia = (glucemia >= 180).sum()

                valor_final = (total/total_glucemia)*100 if total_glucemia != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "GLUCEMIA": ["RESUMEN GLOBAL niveles glucemia"],
                    "TRATAMIENTO_INSULINA": [f"Total: {insulina.sum()}"],
                    "TOTAL_GLUCEMIA": [f"Total: {total_glucemia}"],
                    "TOTAL_GLUCEMIA_INSULINA": [f"Total: {total}"],
                    "INDICE_MANTENIMIENTO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["GLUCEMIA", "TRATAMIENTO_INSULINA"], [glucemia, insulina], 
                    f"indicador_glucemia_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Mantenimiento de Niveles de Glucemia:Es un indicador de proceso que mide el porcentaje de pacientes en " \
        "los que se mantiene una glucemia capilar de 150, con el fin de evitar tanto la hiperglucemia como la hipoglucemia " \
        "grave y reducir así la morbi-mortalidad asociada.", ocultar=ocultar)

    def resucitacion_precoz_sepsis(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "SEPSIS" not in df.columns:
                    raise ValueError(f"Falta la columna 'Sepsis' en {nombre}")
                
                if "SHOCK_SEPTICO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Shock Septico' en {nombre}")
                
                if "PAM_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'PAM ingreso' en {nombre}")
                
                if "PAM_6H" not in df.columns:
                    raise ValueError(f"Falta la columna 'PAM 6h' en {nombre}")
                
                if "PAM_24H" not in df.columns:
                    raise ValueError(f"Falta la columna 'PAM 24h' en {nombre}")
                
                if "DIURESIS_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Diuresis Ingreso' en {nombre}")
                
                if "DIURESIS_6H" not in df.columns:
                    raise ValueError(f"Falta la columna 'Diuresis 6h' en {nombre}")
                
                if "DIURESIS_24H" not in df.columns:
                    raise ValueError(f"Falta la columna 'Diuresis 24h' en {nombre}")
                
                if "LACTATO_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Lactato Ingreso' en {nombre}")
                
                if "LACTATO_6H" not in df.columns:
                    raise ValueError(f"Falta la columna 'Lactato 6h' en {nombre}")
                
                if "LACTATO_24H" not in df.columns:
                    raise ValueError(f"Falta la columna 'Lactato 24h' en {nombre}")
                
                if "FECHA_ALTA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha Alta' en {nombre}")
            
                #Logica de calculo
                sepsis = df["SEPSIS"].fillna(False)
                ss = df["SHOCK_SEPTICO"].fillna(False)
                pam_ingreso = pd.to_numeric(df["PAM_INGRESO"], errors="coerce")
                pam_6 = pd.to_numeric(df["PAM_6H"], errors="coerce")
                pam_24 = pd.to_numeric(df["PAM_24H"], errors="coerce")
                diuresis_ingreso = pd.to_numeric(df["DIURESIS_INGRESO"], errors="coerce")
                diuresis_6 = pd.to_numeric(df["DIURESIS_6H"], errors="coerce")
                diuresis_24 = pd.to_numeric(df["DIURESIS_24H"], errors="coerce")
                lactato_ingreso = pd.to_numeric(df["LACTATO_INGRESO"], errors="coerce")
                lactato_6 = pd.to_numeric(df["LACTATO_6H"], errors="coerce")
                lactato_24 = pd.to_numeric(df["LACTATO_24H"], errors="coerce")
                alta = pd.to_datetime(df["FECHA_ALTA"], format="%d/%m/%Y", errors="coerce")

                #Calculamos la resucitacion con la PAM, Diuresis y el Lactato mayores a un numero o cambio del 50% en lactato
                resucitacion_ingreso = ((pam_ingreso > 65)|(diuresis_ingreso > 0.5)|((lactato_ingreso > 0.9) & (lactato_ingreso < 1.1)))
                resucitacion_6 = ((pam_6 > 65)|(diuresis_6 > 0.5)|(((lactato_6 > 0.9) & (lactato_6 < 1.1))|((lactato_ingreso*0.5) >= lactato_6)))
                resucitacion_24 = ((pam_24 > 65)|(diuresis_24 > 0.5)|(((lactato_24 > 0.9) & (lactato_24 < 1.1))|((lactato_6*0.5) >= lactato_24)))

                #Donde tengan sepsis, SS y se de la resucitacion precoz
                numerador = ((sepsis|ss)&(resucitacion_ingreso|resucitacion_6|resucitacion_24)).sum()

                #Enfermos que tengan sepsis, SS y esten dados de alta
                denominador = ((sepsis|ss)&(alta.notna())).sum()

                valor_final = (numerador/denominador)*100 if denominador != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "RESICITACION_PRECOS_SEPSIS": ["RESUMEN GLOBAL resucitacion precoz con sepsis"],
                    "SEPSIS_SS_RESUCITACION": [f"Total:{numerador}"],
                    "SEPSIS_SS_ALTA": [f"Total:{denominador}"],
                    "RESUCITACION_INGRESO": [f"Total:{resucitacion_ingreso.sum()}"],
                    "RESUCITACION_6H": [f"Total:{resucitacion_6.sum()}"],
                    "RESUCITACION_24H": [f"Total:{resucitacion_24.sum()}"],
                    "INDICADOR_RESUCITACION": [f"Total: {float(valor_final)}"],
                    "SEPSIS": [f"Total: {sepsis.sum()}"],
                    "SHOCK_SEPTICO": [f"Total: {ss.sum()}"],
                    "PAM_INGRESO": [f"Total: {(pam_ingreso > 65).sum()}"],
                    "PAM_6H": [f"Total: {(pam_6 > 65).sum()}"],
                    "PAM_24H": [f"Total: {(pam_24 > 65).sum()}"],
                    "DIURESIS_INGRESO": [f"Total: {(diuresis_ingreso > 0.5).sum()}"],
                    "DIURESIS_6H": [f"Total: {(diuresis_6 > 0.5).sum()}"],
                    "DIURESIS_24H": [f"Total: {(diuresis_24 > 0.5).sum()}"],
                    "LACTATO_INGRESO": [f"Total: {((lactato_ingreso > 0.9) & (lactato_ingreso < 1.1)).sum()}"],
                    "LACTATO_6H": [f"Total: {((lactato_6 > 0.9) & (lactato_6 < 1.1)).sum()}"],
                    "LACTATO_24H": [f"Total: {((lactato_24 > 0.9) & (lactato_24 < 1.1)).sum()}"],
                    "LACTATO_VARIACION_6": [f"Total: {((lactato_ingreso*0.5) >= lactato_6).sum()}"],
                    "LACTATO_VARIACION_24": [f"Total: {((lactato_6*0.5) >= lactato_24).sum()}"],
                    "FECHA_ALTA": [f"Total: {(alta.notna()).sum()}"]
                }
                self.csv_metodo(
                    data_resumen, ["SEPSIS","SHOCK_SEPTICO","PAM_INGRESO","PAM_6H","PAM_24H","DIURESIS_INGRESO","DIURESIS_6H",
                                   "DIURESIS_24H","LACTATO_INGRESO","LACTATO_6H","LACTATO_24H","LACTATO_VARIACION_6",
                                   "LACTATO_VARIACION_24","FECHA_ALTA"], 
                    [sepsis,ss,pam_ingreso,pam_6,pam_24,diuresis_ingreso,diuresis_6,
                     diuresis_24,lactato_ingreso,lactato_6,lactato_24,
                     lactato_ingreso.astype(str) + " - " + lactato_6.astype(str),lactato_6.astype(str) + " - " + lactato_24.astype(str),alta], 
                    f"indicador_resucitacion_precoz_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Resucitación Precoz de la Sepsis:Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con sepsis o shock séptico que reciben el paquete de medidas de tratamiento inicial (administración de fluidos y " \
        "vasopresores) en los plazos establecidos, con el fin de restaurar la perfusión tisular y reducir la mortalidad.", ocultar=ocultar)

    def traslado_intrahospitalario(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "LISTADO_DE_VERIFICACION" not in df.columns:
                    raise ValueError(f"Falta la columna 'Listado de verificacion' en {nombre}")
                
                if "TRASLADO_INTRAHOSPITALARIO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Traslado intrahospitalario' en {nombre}")
            
                #Logica de calculo
                traslado = df["TRASLADO_INTRAHOSPITALARIO"].fillna(False)
                listado = df["LISTADO_DE_VERIFICACION"].fillna(False)
                num_traslado = traslado.sum()

                #Aquellos que tengan traslado y listado
                num_listado = ((listado == True) & (traslado == True)).sum()

                valor_final = (num_listado/num_traslado)*100 if num_traslado != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "LISTADO_DE_VERIFICACION": ["RESUMEN GLOBAL listado trsalado"],
                    "TRASLADO_INTRAHOSPITALARIO": [f"Total: {num_traslado}"],
                    "TOTAL_LISTADO_TRASLADO": [f"Total: {num_listado}"],
                    "INDICE_LISTADO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["LISTADO_DE_VERIFICACION", "TRASLADO_INTRAHOSPITALARIO"], [listado, traslado], 
                    f"indicador_listado_traslado_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Traslado Intrahospitalario:Es un indicador de proceso que mide el porcentaje de traslados de pacientes " \
        "críticos fuera de la UCI (a pruebas de imagen o quirófano) realizados utilizando un listado de verificación (check-list) " \
        "estandarizado, con el fin de minimizar los eventos adversos y garantizar la seguridad durante el transporte.", ocultar=ocultar)

    def tratamiento_empirico_infeccion(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "TRATAMIENTO_ADECUADO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Tratamiento Adecuado' en {nombre}")
                
                if "COBERTURA_EMPIRICA_COMPLETA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Cobertura Empirica Completa' en {nombre}")
                
                if "RESISTENCIA_ANTIBIOTICOS" not in df.columns:
                    raise ValueError(f"Falta la columna 'Resistencia antibioticos' en {nombre}")
                
                if "SEPSIS" not in df.columns:
                    raise ValueError(f"Falta la columna 'Sepsis' en {nombre}")
                
                if "SHOCK_SEPTICO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Shock Septico' en {nombre}")
            
                #Logica de calculo
                adec = df["TRATAMIENTO_ADECUADO"].fillna(False)
                completa = df["COBERTURA_EMPIRICA_COMPLETA"].fillna(False)
                resistencia = df["RESISTENCIA_ANTIBIOTICOS"].fillna(False)
                sepsis = df["SEPSIS"].fillna(False)
                ss = df["SHOCK_SEPTICO"].fillna(False)

                #Aquellos que tenga ss o sepsis
                num_infeccion = (sepsis | ss).sum()

                #Aquellos que sea adecuado, no presenten resistencia y sea completa
                trat_adecuado = ((adec & ~resistencia & completa) & (sepsis | ss)).sum()
                    
                valor_final = (trat_adecuado/num_infeccion)*100 if num_infeccion != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "IND_TRATAMIENTO_ADECUADO": ["RESUMEN GLOBAL tratamiento empirico"],
                    "SIN_RESISTENCIA": [f"Total: {(~resistencia & (ss|sepsis)).sum()}"],
                    "TRATAMIENTO_ADECUADO": [f"Total: {(adec & (ss|sepsis)).sum()}"],
                    "COBERTURA_EMPIRICA_COMPLETA": [f"Total: {(completa & (ss|sepsis)).sum()}"],
                    "TOTAL_INFECCIONES": [f"Total: {num_infeccion}"],
                    "TOTAL_TRAT_ADECUADO": [f"Total: {trat_adecuado}"],
                    "INDICE_TRAT_ADECUADO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["SIN_RESISTENCIA", "TRATAMIENTO_ADECUADO", "COBERTURA_EMPIRICA_COMPLETA"], [resistencia, adec, completa], 
                    f"indicador_trat_adecuado_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Tratamiento Empírico Adecuado:Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con sospecha de infección grave que reciben una terapia antibiótica inicial ajustada a las guías clínicas y a los " \
        "mapas de resistencias locales en menos de una hora, con el fin de reducir drásticamente la mortalidad y la " \
        "disfunción orgánica", ocultar=ocultar)

    def neumonia_asociada_vmi(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "EPISODIOS_NAV" not in df.columns:
                    raise ValueError(f"Falta la columna 'Episodios NAV' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
            
                #Logica de calculo
                nav = df["EPISODIOS_NAV"].fillna(False)
                vmi = pd.to_numeric(df["DIAS_VMI"], errors="coerce")

                #Simplemente hay que hacer el calculo
                valor_final = (nav.sum()/vmi.sum())*1000 if vmi.sum() != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "EPISODIOS_NAV": ["RESUMEN GLOBAL nuemonia asociada a VMI"],
                    "DIAS_VMI": [f"Total: {vmi.sum()}"],
                    "TOTAL_NAV": [f"Total: {nav.sum()}"],
                    "INDICE_NAV": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["TOTAL_NAV", "DIAS_VMI"], [nav, vmi], 
                    f"indicador_nav_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Neumonia Asociada a VMI:Es un indicador de seguridad que mide el número de episodios " \
        "de neumonía desarrollados por cada 1.000 días de ventilación mecánica, con el " \
        "fin de evaluar la eficacia de las medidas preventivas y reducir las complicaciones infecciosas del paciente crítico", ocultar=ocultar)

    def reintubacion(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "REGISTRO_INTUBACIONES" not in df.columns:
                    raise ValueError(f"Falta la columna 'Registro Intubaciones' en {nombre}")
                
                if "EXTUBACION_PROGRAMADA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Extubacion Programada' en {nombre}")
            
                #Logica de calculo
                intuba = df["REGISTRO_INTUBACIONES"].fillna(pd.NA)
                extuba = df["EXTUBACION_PROGRAMADA"].fillna(False)

                #Aquellos que contengan mas de un registro en intubaciones
                reintubaciones = (intuba.astype(str).str.contains(";", na=False)).sum()
                num_extuba = ((intuba.notna())&(extuba == True)).sum()

                valor_final = (reintubaciones/num_extuba)*100 if num_extuba != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "REGISTRO_INTUBACIONES": ["RESUMEN GLOBAL reintubaciones"],
                    "EXTUBACION_PROGRAMADA": [f"Total: {num_extuba}"],
                    "TOTAL_INTUBACIONES": [f"Total: {(intuba.notna()).sum()}"],
                    "TOTAL_REINTUBACIONES": [f"Total: {reintubaciones}"],
                    "INDICE_REINTUBACIONES": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["REGISTRO_INTUBACIONES", "EXTUBACION_PROGRAMADA"], [intuba, extuba], 
                    f"indicador_reintubaciones_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Reintubación:Es un indicador de resultado que mide el porcentaje de pacientes que requieren " \
        "la inserción de un tubo endotraqueal posterior a una extubación planificada, con el objetivo de evaluar " \
        "el éxito del destete y evitar el aumento de la morbimortalidad asociada al fracaso de la extubación.", ocultar=ocultar)
    
    def especialidad_ingreso(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "ESPECIALIDAD_DE_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Especialidad de ingreso' en {nombre}")
            
                #Logica de calculo
                especialidad = df["ESPECIALIDAD_DE_INGRESO"].fillna("No especificada")
                #Metodo de pandas que agrupa y contabiliza las apariciones(normalizadas)
                valores = especialidad.value_counts(normalize=True)

                #Esta lista la creamos para guardar todas las especialidades de un año
                lista_dic = []
                for (nomb,valor) in zip (valores.index, valores.values):
                    #Creamos un diccionario con la especialidad y su valor
                    diccionario = {"especialidad": f"{self.normalizar_frame(nomb, esp_ingreso=True)}_{self.encontrar_año(nombre)}", "indicador": round(float(valor * 100), 4)}
                    lista_dic.append(diccionario)
                #Introducimos la lista de diccionarios al resultado esto nos permite que cada año reciba una lista con sus indicadores
                resultado.append(lista_dic)
                
                #Creamos un df con el metodo reset_index() para poder usarlos en el csv a descargar
                df_temp = valores.reset_index()
                df_temp.columns = ["nombre", "conteo"] 

                data_resumen = {
                    "ESPECIALIDAD_DE_INGRESO": ["RESUMEN GLOBAL ingresos por especialidad"],
                    "ESPECIALIDAD": [f"Total: {len(df_temp["nombre"])}"],
                    "TOTAL_POR_ESPECIALIDAD": [f"Total: {len(df)}"],
                    "INDICE_ESPECIALIDAD": [f"Total: {(df_temp["conteo"] * 100).sum()}"]
                }
                self.csv_metodo(
                    data_resumen, ["ESPECIALIDAD_DE_INGRESO", "ESPECIALIDAD", "TOTAL_POR_ESPECIALIDAD", "INDICE_ESPECIALIDAD"], 
                    [especialidad, df_temp["nombre"], df_temp["conteo"] * len(df), df_temp["conteo"] * 100], 
                    f"indicador_especialidad_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        #Flag que nos permite identificar cuando se activa este indicador para modificar los graficos
        self.ind_especi = True
        self.final(resultado, "Especialidades con Mayores Ingresos:Identifica la especialidad médica o quirúrgica que genera " \
        "el mayor número de ingresos en el Servicio de Medicina Intensiva (SMI). Esto es fundamental para la planificación de " \
        "recursos, la formación del personal y la creación de protocolos específicos.", ocultar=ocultar)
        
    def profilaxis_ulcera_enfermos_NE(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "TRATAMIENTO_CORTICOIDES" not in df.columns:
                    raise ValueError(f"Falta la columna 'Tratamiento Corticoides' en {nombre}")
                
                if "ANTECEDENTES_HEMORRAGIA_GI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Antecedentes Hemorragia GI' en {nombre}")
                
                if "COAGULOPATIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Coagulopatia' en {nombre}")
                
                if "INSUFICIENCIA_RENAL" not in df.columns:
                    raise ValueError(f"Falta la columna 'Insuficiencia Renal' en {nombre}")
                
                if "INSUFICIENCIA_HEPATICA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Insuficiencia Hepatica' en {nombre}")
                
                if "FECHA_INICIO_NE" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha Inicio NE' en {nombre}")
                
                if "OMEPRAZOL" not in df.columns:
                    raise ValueError(f"Falta la columna 'Omeprazol' en {nombre}")
                        
                #Logica de calculo
                corticoides = df["TRATAMIENTO_CORTICOIDES"].fillna(False)
                hemorragia = df["ANTECEDENTES_HEMORRAGIA_GI"].fillna(False)
                coagulopatia = df["COAGULOPATIA"].fillna(False)
                renal = df["INSUFICIENCIA_RENAL"].fillna(False)
                hepatica = df["INSUFICIENCIA_HEPATICA"].fillna(False)
                ne = pd.to_datetime(df["FECHA_INICIO_NE"], format="%d/%m/%Y", errors="coerce")
                profilaxis = df["OMEPRAZOL"].fillna(False)

                #Calculamos la hgi que tiene los siguiente componentes
                hgi = (corticoides|hemorragia|coagulopatia|renal|hepatica)
                #Donde haya HGI, nutricion enteral y no haya profilaxis
                ne_profilaxis_hgi = ((hgi == True)&(ne.notna())&(profilaxis == False)).sum()
                #Donde haya HGI y nutricion enteral
                ne_hgi = ((hgi == True)&(ne.notna())).sum()

                valor_final = (ne_profilaxis_hgi/ne_hgi)*100 if ne_hgi != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "HGI_NE_NOPROFILAXIS": ["RESUMEN GLOBAL profilaxis de ulcera con NE"],
                    "HGI_NE_NOPROFILAXIS_TOTAL": [f"Total: {ne_profilaxis_hgi}"],
                    "HGI_NE": [f"Total: {ne_hgi}"],
                    "HGI": [f"Total: {hgi.sum()}"],
                    "CORTICOIDES": [f"Total: {corticoides.sum()}"],
                    "ANTECEDENTES_HEMORRAGIA_GI": [f"Total: {hemorragia.sum()}"],
                    "COAGULOPATIA": [f"Total: {coagulopatia.sum()}"],
                    "INSUFICIENCIA_RENAL": [f"Total: {renal.sum()}"],
                    "INSUFICIENCIA_HEPATICA": [f"Total: {hepatica.sum()}"],
                    "FECHA_INICIO_NE": [f"Total: {(ne.notna()).sum()}"],
                    "PROFILAXIS_HGI": [f"Total: {profilaxis.sum()}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["CORTICOIDES", "ANTECEDENTES_HEMORRAGIA_GI", "COAGULOPATIA", 
                                   "INSUFICIENCIA_RENAL", "INSUFICIENCIA_HEPATICA", "FECHA_INICIO_NE", "PROFILAXIS_HGI"], 
                                  [corticoides, hemorragia, coagulopatia, renal, hepatica,  ne, profilaxis], 
                    f"indicador_profilaxis_ulceras_NE_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Profilaxis de Úlcera por Estrés con NE:Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con nutrición enteral que no reciben fármacos supresores del ácido gástrico innecesariamente, con el fin de " \
        "evitar efectos adversos, ya que la propia nutrición se considera protectora.", ocultar=ocultar)

    def sedacion_adecuada(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "RASS" not in df.columns:
                    raise ValueError(f"Falta la columna 'RASS' en {nombre}")
                
                if "BIS" not in df.columns:
                    raise ValueError(f"Falta la columna 'BIS' en {nombre}")
                
                if "RASS_OBJETIVO" not in df.columns:
                    raise ValueError(f"Falta la columna 'RASS objetivo' en {nombre}")
                
                if "BIS_OBJETIVO" not in df.columns:
                    raise ValueError(f"Falta la columna 'BIS objetivo' en {nombre}")
                
                if "VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'VMI' en {nombre}")
                
                #Logica de calculo
                rass = pd.to_numeric(df["RASS"], errors="coerce")
                bis = pd.to_numeric(df["BIS"], errors="coerce")
                rass_objetivo = pd.to_numeric(df["RASS_OBJETIVO"], errors="coerce")
                bis_objetivo = pd.to_numeric(df["BIS_OBJETIVO"], errors="coerce")
                vmi = df["VMI"].fillna(False)

                #Sedacion adecuada 
                rass_adecuada = ((rass <= rass_objetivo + 1) & (rass >= rass_objetivo - 1))
                bis_adecuada = ((bis <= bis_objetivo + 5) & (bis >= bis_objetivo - 5))
                sedacion_adecuada = (rass_adecuada | bis_adecuada).sum()
                                     
                #Total sedacion 
                sedacion = (vmi).sum()

                valor_final = (sedacion_adecuada/sedacion)*100 if sedacion != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "SEDACION_ADECUADA_INDICADOR": ["RESUMEN GLOBAL sedacion adecuada"],
                    "SEDACION_ADECUADA": [f"Total: {sedacion_adecuada}"],
                    "TOTAL_SEDACION": [f"Total: {sedacion}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"],
                    "RASS": [f"Total: {(rass.notna()).sum()}"],
                    "RASS_OBJETIVO": [f"Total: {(rass_objetivo.notna()).sum()}"],
                    "RASS_ADECUADA": [f"Total: {rass_adecuada.sum()}"],
                    "BIS": [f"Total: {(bis.notna()).sum()}"],
                    "BIS_OBJETIVO": [f"Total: {(bis_objetivo.notna()).sum()}"],
                    "BIS_ADECUADA": [f"Total: {bis_adecuada.sum()}"],
                }
                self.csv_metodo(
                    data_resumen, ["RASS","RASS_OBJETIVO","RASS_ADECUADA","BIS","BIS_OBJETIVO", "BIS_ADECUADA"], 
                    [rass,rass_objetivo,rass[rass_adecuada],bis,bis_objetivo,bis[bis_adecuada]], 
                    f"indicador_sedacion_adecuada_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Sedación Adecuada:Sedación adecuada es el mantenimiento de " \
        "los resultados de las escalas de sedación dentro del rango prescrito (objetivo) para ese enfermo en particular.", ocultar=ocultar)

    def ingresos_urgentes(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "INGRESO_POR_URGENCIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Ingreso por Urgencia' en {nombre}")
                
                #Logica de calculo
                urgencia = df["INGRESO_POR_URGENCIA"].fillna(False)

                #Total de urgentes y de pacientes
                total_urgentes = (urgencia).sum()
                total = len(df)


                valor_final = (total_urgentes/total)*100 if total != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "INGRESOS_URGENTES": ["RESUMEN GLOBAL ingresos urgentes"],
                    "INGRESO_POR_URGENCIA": [f"Total: {total_urgentes}"],
                    "PACIENTES_TOTALES": [f"Total: {total}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["INGRESOS_URGENTES"], [urgencia], 
                    f"indicador_ingreso_urgente_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Ingresos Urgentes:Indicador de estructura y proceso que " \
        "mide la proporción de pacientes que ingresan en el Servicio de Medicina Intensiva (SMI) de forma no programada. " \
        "Estos ingresos suelen proceder de Urgencias, plantas de hospitalización "
        "(tras un deterioro agudo) o tras cirugías de emergencia.", ocultar=ocultar)

    def adversos_traslado(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "TRASLADO_INTRAHOSPITALARIO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Traslado Intrahospitalario' en {nombre}")
                
                if "EVENTOS_ADVERSOS_TRASLADO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Eventos Adversos Traslado' en {nombre}")
                
                #Logica de calculo
                traslado = df["TRASLADO_INTRAHOSPITALARIO"].fillna(False)
                adverso = df["EVENTOS_ADVERSOS_TRASLADO"].fillna(False)                

                #Total de traslados
                total_traslado = traslado.sum()
                #Total de eventos adversos
                total_adversos = (traslado&adverso).sum()


                valor_final = (total_adversos/total_traslado)*100 if total_traslado != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "EVENTO_ADVERSO": ["RESUMEN GLOBAL evento adverso traslado"],
                    "TRASLADO_INTRAHOSPITALARIO": [f"Total: {total_traslado}"],
                    "EVENTOS_ADVERSOS_TRASLADO": [f"Total: {total_adversos}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["TRASLADO_INTRAHOSPITALARIO", "EVENTOS_ADVERSOS_TRASLADO"], [traslado,adverso], 
                    f"indicador_adverso_traslado_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Eventos Adversos Durante el Traslado:Es un indicador de seguridad que mide la incidencia de " \
        "incidentes o accidentes que ocurren durante el traslado de un paciente crítico fuera de la UCI (traslados intrahospitalarios), " \
        "ya sea para pruebas diagnósticas (TAC, Resonancia) o intervenciones (Quirófano).", ocultar=ocultar)

    def ne_precoz(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "FECHA_INICIO_NE" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha Inicio NE' en {nombre}")
                
                if "FECHA_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha Ingreso' en {nombre}")
                
                #Logica de calculo
                #Conversion a fechas
                ne = pd.to_datetime(df["FECHA_INICIO_NE"], format="%d/%m/%Y", errors="coerce")
                ingreso = pd.to_datetime(df["FECHA_INGRESO"], format="%d/%m/%Y", errors="coerce")

                #Usamos total_seconds() / 3600 para que si pasan 3 dias, nos de 72 horas.
                diferencia = (ne - ingreso).dt.total_seconds() / 3600

                #Filtramos donde la diferencia sea menor a 48 y sumamos los casos
                precoz = ((diferencia >= 0) & (diferencia <= 48)).sum()
                total_ne = (ne.notna()).sum()


                valor_final = (precoz/total_ne)*100 if total_ne != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "NE_PRECOZ": ["RESUMEN GLOBAL nutricion enteral precoz"],
                    "FECHA_INGRESO": [f"Total: {(ingreso.notna()).sum()}"],
                    "FECHA_INICIO_NE": [f"Total: {total_ne}"],
                    "DIFERENCIA": [f"Total: {precoz}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["FECHA_INGRESO", "FECHA_INICIO_NE","DIFERENCIA"], [ingreso,ne,diferencia], 
                    f"indicador_ne_precoz_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Nutrición Enteral Precoz:Es un indicador de proceso que mide la capacidad " \
        "del servicio para iniciar el soporte nutricional por vía digestiva (enteral) en las primeras 48 horas desde " \
        "el ingreso del paciente crítico, siempre que no existan contraindicaciones.", ocultar=ocultar)

    def sobretransfusion_hematies(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "ACTOS_TRANSFUSIONALES" not in df.columns:
                    raise ValueError(f"Falta la columna 'Actos Transfusionales' en {nombre}")
                
                if "SANGRADO_ACTIVO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Sangrado Activo' en {nombre}")
                
                if "CANTIDAD_TRANSFUSION_DIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Cantidad Transfusion Dia' en {nombre}")
                
                #Logica de calculo
                trans = df["ACTOS_TRANSFUSIONALES"].fillna(False)
                sangrado = df["SANGRADO_ACTIVO"].fillna(False)
                cantidad_trans = pd.to_numeric(df["CANTIDAD_TRANSFUSION_DIA"], errors="coerce")

                #Actos trasnfusionales, sin sangrado en los que la cantidad de CH > 1
                numerador = (trans&~sangrado&(cantidad_trans > 1)).sum()

                #Actos trasnfusionales, sin sangrado
                denominador = (trans&~sangrado).sum()

                valor_final = (numerador/denominador)*100 if denominador != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "SOBRETRANSFUSION_HEMATIES": ["RESUMEN GLOBAL sobretransfusion hematies"],
                    "ACTOS_TRANSFUSIONALES": [f"Total: {trans.sum()}"],
                    "SANGRADO_ACTIVO": [f"Total: {~sangrado.sum()}"],
                    "CANTIDAD_TRANSFUSION_DIA": [f"Total: {(cantidad_trans > 1).sum()}"],
                    "TRANS_SIN_SANGRADO_CH>1": [f"Total: {numerador}"],
                    "TRANS_SIN_SANGRADO": [f"Total: {denominador}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["ACTOS_TRANSFUSIONALES", "SANGRADO_ACTIVO","CANTIDAD_TRANSFUSION_DIA"], [trans,sangrado,cantidad_trans], 
                    f"indicador_sobretransfusion_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Sobretransfusión de Hematíes:Es un indicador de proceso que mide el porcentaje de " \
        "pacientes que reciben una transfusión de concentrados de hematíes (CH) cuando se trasfunde " \
        "más de una unidad sin reevaluar al paciente.", ocultar=ocultar)
    
    def retirada_accidental(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "EXTUBACION_POR_MANIOBRAS" not in df.columns:
                    raise ValueError(f"Falta la columna 'Extubacion por Maniobras' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
                
                #Logica de calculo
                extubacion = df["EXTUBACION_POR_MANIOBRAS"].fillna(False)
                dias = pd.to_numeric(df["DIAS_VMI"], errors="coerce")

                #Numero extubaciones
                num_extubaciones = extubacion.sum()
                #Numero de TET = VMI
                num_vmi = dias.sum()

                valor_final = (num_extubaciones/num_vmi)*1000 if num_vmi != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "RETIRADA_ACCIDENTAL": ["RESUMEN GLOBAL retirada accidental por maniobras"],
                    "EXTUBACION_POR_MANIOBRAS": [f"Total: {num_extubaciones}"],
                    "DIAS_VMI": [f"Total: {num_vmi}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["EXTUBACION_POR_MANIOBRAS", "DIAS_VMI"], [extubacion,dias], 
                    f"indicador_retirada_accidental_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "TET por Maniobras:Mide el número de episodios de salida no planificada del " \
        "tubo endotraqueal (TET) en pacientes sometidos a ventilación mecánica. Se considera una de las complicaciones más graves de " \
        "la vía aérea en la UCI debido al riesgo de hipoxia, parada cardiorrespiratoria o trauma laríngeo", ocultar=ocultar)

    def bacteriemia(self, ocultar = False):
        resultado = self.limpieza()

        try:
            for (dataframe_memoria, nombre) in zip(self._dataframes_memoria, self.nombres_archivos):
                df = dataframe_memoria.copy()
                df = df.replace({"True": True, "true": True, "False": False, "false": False, "None": pd.NA, "": pd.NA})
                
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "NUMERO_EPISODIOS_BACTERIEMIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Numero Episodios Bacteriemia' en {nombre}")
                
                if "NUMERO_TOTAL_DE_DIAS_CVC" not in df.columns:
                    raise ValueError(f"Falta la columna 'Numero total de días CVC' en {nombre}")
                
                #Logica de calculo
                bacteriemia = pd.to_numeric(df["NUMERO_EPISODIOS_BACTERIEMIA"], errors="coerce")
                cvc = pd.to_numeric(df["NUMERO_TOTAL_DE_DIAS_CVC"], errors="coerce")

                #Numero bacteriemia
                num_bacteriemia = bacteriemia.sum()
                #Numero de dias CVS
                num_cvc = cvc.sum()

                valor_final = (num_bacteriemia/num_cvc)*1000 if num_cvc != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "EPISODIOS_BACTERIEMIA": ["RESUMEN GLOBAL bacteriemia relacionada a CVC"],
                    "NUMERO_EPISODIOS_BACTERIEMIA": [f"Total: {num_bacteriemia}"],
                    "NUMERO_TOTAL_DE_DIAS_CVC": [f"Total: {num_cvc}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["NUMERO_EPISODIOS_BACTERIEMIA", "NUMERO_TOTAL_DE_DIAS_CVC"], [bacteriemia,cvc], 
                    f"bacteriemia_CVC_{self.encontrar_año(nombre)}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Bacteriemia relacionada a CVC:Mide los episodios de infección del torrente sanguíneo " \
        "relacionados con el uso de catéteres venosos centrales. Es una de las complicaciones más importantes en la UCI, " \
        "asociada a un incremento en la mortalidad y días de estancia. Estándar esperado: < 3 episodios por 1.000 días de CVC.", ocultar=ocultar)

    #Funcion que hace los calculos
    def calculos_estadisticos(self, eje_x, eje_y, individual = False):
        #Calculamos la media y  la desviacion
        media = np.mean(eje_y)
        desviacion = np.std(eje_y)

        #Error tipico
        error_tipico = desviacion / np.sqrt(len(eje_y))

        x_numerico = np.array(range(1,len(eje_x)+1))
        #Calculamos la pendiente y punto de corte, con deg=1 permite obtener una recta
        tend=np.polyfit(x_numerico, eje_y, deg=1)

        #Si la variacion entre el año mas alto y el mas bajo es minima
        if max(eje_y) - min(eje_y) < 1.0:
            r2 = 0.0
            #Forzamos la linea a ser totalmente plana en la media
            y_tendencia = [media] * len(eje_x)
        else:
            #Calculamos la recta con su formula
            y_tendencia = tend[0] * x_numerico + tend[1]
            #Calculamos la r2
            r2 = r2_score(eje_y, y_tendencia)

        #Si llamamos a la funcion desde los indicadores individuales devolvemos los puntos de la tendencia, el error, la pendiente y la r2
        if individual == True:
            return y_tendencia, error_tipico, tend[0], r2
        
        #Si es para dibujar graficos devolvemos lo necesario
        else:
            return media, desviacion, error_tipico, tend[0], y_tendencia, r2
    
    #Funcion para realizar los graficos con matplotlib
    def grafico(self, eje_x, eje_y, texto, media, desviacion, error_tipico, tend, y_tendencia, r2):
        #Creamos el objeto io
        grafico_bytes = io.BytesIO()
        
        #Claves que determinan el color
        claves = {
            "Mortalidad Estandarizada": True,                 #Bajar es bueno (menor mortalidad)
            "Reingresos no Programados": True,                #Bajar es bueno (menor tasa de fracaso al alta)
            "Incidencia de Barotrauma": True,                 #Bajar es bueno (complicacion)
            "Posición Semiincorporada con VMI": False,        #Subir es bueno (adherencia a medida preventiva)
            "Incidencias Úlcera por Presión UPP": True,       #Bajar es bueno (complicacion)
            "Interrupción Diaria de la Sedación": False,      #Subir es bueno (adherencia a protocolo)
            "Prevención Enfermedad Tromboembólica": False,    #Subir es bueno (adherencia a profilaxis)
            "Mantenimiento de Niveles de Glucemia": False,    #Subir es bueno (mayor % de pacientes en rango)
            "Resucitación Precoz de la Sepsis": False,        #Subir es bueno (adherencia a las guias)
            "Traslado Intrahospitalario": False,              #Subir es bueno (asumiendo que mide adecuacion/seguridad del protocolo)
            "Tratamiento Empírico Adecuado": False,           #Subir es bueno (mayor % de acierto empirico)
            "Neumonia Asociada a VMI": True,                  #Bajar es bueno (infeccion nosocomial)
            "Reintubación": True,                             #Bajar es bueno (fracaso de extubacion)
            "Profilaxis de Úlcera por Estrés con NE": False,  #Subir es bueno (adecuacion de la profilaxis)
            "Sedación Adecuada": False,                       #Subir es bueno (mayor % de tiempo en objetivo)
            "Ingresos Urgentes": True,                        #Bajar es bueno (si mide retrasos o ingresos imprevistos)
            "Eventos Adversos Durante el Traslado": True,     #Bajar es bueno (complicaciones)
            "Nutrición Enteral Precoz": False,                #Subir es bueno (adherencia a protocolo)
            "Sobretransfusión de Hematíes": True,             #Bajar es bueno (evitar transfusiones innecesarias)
            "TET por Maniobras": True,                        #Bajar es bueno (extubacion accidental/retirada, complicacion)
            "Bacteriemia relacionada a CVC": True             #Bajar es bueno (infeccion nosocomial)
        }

        #Regla de las 2 Sigmas para dar color a las columnas
        colores = []

        for valor in eje_y:
            if valor > media + 2 * desviacion:
                if texto not in claves.keys() or claves[texto] == True:
                    colores.append("red")
                else:
                    colores.append("green")
                
            elif valor < media - 2 * desviacion:
                if texto not in claves.keys() or claves[texto] == True:
                    colores.append("green")
                else:
                    colores.append("red") 

            else: colores.append(Color.ACENTO.value) 

        #Creacion del grafico
        fig, ax = plt.subplots(figsize=(5,4))

        #Si se ha seleccionado el de barras o el de lineas
        if self.ind_grafico == "barras":
            #zorder=2 para que los datos se pinten por delante del pasillo
            ax.bar(x=eje_x, height=eje_y, color=colores, zorder=2)
        else:
            #Dibujamos las lineas
            ax.plot(eje_x, eje_y, color=Color.ACENTO.value, zorder=2)

            #Buscamos los eventos centinela
            for i, color_año in enumerate(colores):
                #Si el color no es el color normal, significa que hay alerta
                if color_año != Color.ACENTO.value: 
                    #Pintamos una linea vertical discontinua en ese año concreto
                    ax.axvline(x=eje_x[i], color=color_año, linestyle="--", alpha=0.6, zorder=1) 
                    #Pintamos el punto de ese año un poco mas grande
                    ax.scatter(eje_x[i], eje_y[i], color=color_año, s=60, zorder=3)

        ax.set_xlabel("Años")
        ax.set_ylabel(texto)
        #Ponemos el titulo con la tendencia y la R2
        ax.set_title(f"{texto}\n(Tendencia: {tend:.4f}, R²: {r2:.4f})")

        #Añadimos un colchon arriba y abajo para que no se apelmazen los graficos
        if min(eje_y) == max(eje_y):
            #Si todos los valores son iguales, sumamos y restamos un margen fijo (+- 1)
            ax.set_ylim(min(eje_y)-1, max(eje_y)+1)
        else:
            # Si hay variacion en los datos, usamos la formula original
            ax.set_ylim(min(eje_y)*0.9, max(eje_y)*1.1)

        #Convertimos y_tendencia a un array de numpy para poder sumarle/restarle el error facilmente
        y_tend_np = np.array(y_tendencia)

        #Pasillo de confianza
        ax.fill_between(
            eje_x,
            #Limite inferior del pasillo
            y_tend_np - error_tipico,
            #Limite superior del pasillo 
            y_tend_np + error_tipico, 
            color="m",
            #Transparencia para que sea sutil
            alpha=0.15,    
            label="Pasillo de Confianza",
            #zorder=1 lo manda al fondo de la grafica
            zorder=1       
        )

        #Dibujamos la pendiente en el grafico
        ax.plot(eje_x, y_tendencia, "m", label="Tendencia", zorder=3)

        #Dibujamos la media
        ax.axhline(media, color="green", linestyle=":", label="Media Histórica", zorder=3)

        #Ajusta automaticamente los subgrafico
        plt.tight_layout()
        #Guardamos el archivo en formato png con alta resolucion
        plt.savefig(grafico_bytes, format="png", dpi=300)
        plt.close(fig)
        return grafico_bytes
    
    #Funcion puente que prepara la interfaz antes del resumen 
    async def preparar_resumen(self):
        #1. Mutamos directamente las variables
        self.manejo_drawer(False)
        self.barra = True
        yield
        
        #2. Mandamos la orden visual a la zona de carga
        yield rx.scroll_to("zona_de_carga")
        
        #3. Obliga al navegador a bajar la pantalla y encender la barra antes de abrir el resumen
        await asyncio.sleep(0.5)
        
        #4. Llamamos a la funcion
        yield self.tabla_resumen()

    def tabla_resumen(self):
        #Limpiamos la memoria de calculos anteriores
        self._memoria_informe = []

        #Recorre los resultados tras ejecutar cada indicador y añadiendo el valor numerico obtenido
        def recuperar_datos():
            x = []
            y = []
            for elem in range(len(self.datos_final)): 
                lista_valores[elem].append(round(self.datos_final[elem]["valor"], 4))
                x.append(self.datos_final[elem]["name"]) 
                y.append(self.datos_final[elem]["valor"])

            #Hacemos los calculos
            media, desviacion, error_tipico, pend_tendencia, y_tendencia, r2 = self.calculos_estadisticos(x, y)
            
            #Guardamos la informacion en memoria
            self._memoria_informe.append({
                "x": x,
                "y": y,
                "titulo": self.texto.split(":")[0],
                "subtitulo": self.texto.split(":")[1],
                "media": media,
                "desviacion": desviacion,
                "error_tipico": error_tipico,
                "pend_tendencia": pend_tendencia,
                "y_tendencia": y_tendencia,
                "r2": r2,
                #Hacemos una copia de la tabla
                "datos_tabla": list(self.datos_final), 
                "es_especialidad": False
            })
        
        #Ensambla todo al terminar:
        #Ejecuta especialidad_ingreso para obtener datos especificos de especialidades
        #Asigna a df_resumen nuevas columnas usando el año como nombre y los valores recolectados como datos
        #El metodo .at[fila, columna] permite el acceso directo a una celda especifica. A diferencia del indexado, si la combinacion de fila o columna no existe, 
        #Pandas expande el DataFrame automaticamente creandolas e insertando el valor sin lanzar errores.
        def parseo_final():
            lista_años = [str(año[0]) for año in lista_valores]
            df_especialidades = pd.DataFrame(index=lista_años)
            df_especialidades.index.name = "Especialidad_Ingreso"

            res = self.especialidad_ingreso(True)
            if res is not None: return res

            #Generamos el diccionario plano de las especialidades de ingreso
            diccionario_datos = self.parseo_especialidad(self.datos_final, resumen=True)
            
            #Recorremos el diccionario para obtener los valores necesarios para graficar
            for especialidad, valores_historicos in diccionario_datos.items():

                #Llamamos a la funcion del calculo para cada especialidad concreta
                media, desviacion, error_tipico, pend_tendencia, y_tendencia, r2 = self.calculos_estadisticos(lista_años, valores_historicos)

                #Añadimos los valores de cada especialidad
                self._memoria_informe.append({
                    "x": lista_años,            
                    "y": valores_historicos,
                    "titulo": f"Especialidad de ingreso: {especialidad}",
                    "subtitulo": self.texto.split(":")[1],
                    "media": media,
                    "desviacion": desviacion,
                    "error_tipico": error_tipico,
                    "pend_tendencia": pend_tendencia,
                    "y_tendencia": y_tendencia,
                    "r2": r2,
                    "datos_tabla": list(zip(lista_años, valores_historicos)), 
                    "es_especialidad": True
                })

            #Ensamblamos el df_resumen
            for elem in range(len(self.datos_final)):
                nombre_columna = lista_valores[elem][0]
                df_resumen[nombre_columna] = lista_valores[elem][1:len(lista_valores[elem])]                

                #Ensamblamos el df_especialidades
                for i in self.datos_final[elem]["valor"]:
                    especialidad = i["especialidad"].split("_")[0]
                    valor_indicador = i["indicador"]
                    df_especialidades.at[nombre_columna, especialidad] = valor_indicador
            
            #Al final, reseteamos el indice para que "Especialidad_Ingreso" vuelva a ser una columna
            df_especialidades = df_especialidades.reset_index()
            return df_resumen, df_especialidades

        #Limpiamos las variables y activamos el booleano    
        self.limpieza()
        self.ind_resumen = True

        #Definimos la columna de indicadores
        data_resumen = {"RESUMEN_INDICADORES": ["Mortalidad Estandarizada", "Reingresos no programados", "Incidencia de barotrauma",
                        "Posicion semiincorporada con VMI", "Incidencias úlcera por presión", "Valoración diaria de la interrupción de la sedación",
                        "Prevención de la enfermedad tromboembólica", "Mantenimiento de niveles de glucemia", "Resucitación precoz de la sepsis",
                        "Traslado intrahospitalario", "Tratamiento empírico adecuado en infección", "Neumonia asociada a ventilacion mecanica",
                        "Reintubación", "Profilaxis de la úlcera por estrés en enfermos con NE", "Sedación adecuada", "Ingresos urgentes",
                        "Eventos adversos durante el traslado intrahospitalario", "Nutrición enteral precoz", 
                        "Sobretransfusión de concentrados de hematies","Retirada accidental del tubo endotraqueal", "Bacteriemia relacionada a CVC"]
                        }
        df_resumen = pd.DataFrame(data_resumen)
        
        #Crea una lista de listas. Cada sublista comienza con el año, se usa para acumular los resultados de ese año especifico
        lista_valores = [[self.encontrar_año(nombre)] for nombre in self.nombres_archivos]
        
        claves = [self.mortalidad_estandarizada, self.reingresos_no_programados, self.incidencia_de_barotrauma, self.posicion_semiincorporada_VMI, 
                  self.incidencia_ulceras_presion, self.valoracion_interrupcion_sedacion, self.prevencion_enfermedad_tromboembolica, self.mantenimiento_niveles_glucemia,
                  self.resucitacion_precoz_sepsis, self.traslado_intrahospitalario, self.tratamiento_empirico_infeccion, self.neumonia_asociada_vmi,
                  self.reintubacion, self.profilaxis_ulcera_enfermos_NE, self.sedacion_adecuada, self.ingresos_urgentes, self.adversos_traslado, self.ne_precoz, 
                  self.sobretransfusion_hematies, self.retirada_accidental, self.bacteriemia]
        
        #Ejecutamos el metodo de calculo con True para el resumen(no dispara la interfaz individual)
        #Si el calculo falla o devuelve algo inesperado, detiene el proceso
        #Toma el resultado recien calculado y lo guarda en la estructura de listas
        for indi in range(len(claves)):
            res = claves[indi](ocultar = True)
            res
            if res is not None:
                self.cerrar_ventana()
                return res
            recuperar_datos()
        
        #Creamos los CSV
        csv_indi, csv_espe = parseo_final()

        #Convierte los nombres de las columnas y las filas de datos del DataFrame a una lista de Python para que Reflex pueda leerlas
        cols_indi = csv_indi.columns.tolist()
        cols_espe = csv_espe.columns.tolist()
        datos_indi = csv_indi.values.tolist()
        datos_espe = csv_espe.values.tolist()

        #Unimos por parejas: [[cols_indi, datos_indi], [cols_espe, datos_espe]]
        self.lista_unida = [
            [cols_indi, datos_indi],
            [cols_espe, datos_espe]
        ]
        self.limpieza()

        #Guardamos los resultados finales. Solo pasamos un texto ("listo") a "valor" para no colapsar la RAM del navegador.
        #Los datos reales de descarga ya estan a salvo en self._csv_final
        self.datos_final.append({"name": "Resumen", "valor": "listo"})
        self.datos_final.append({"name": "Especialidades", "valor": "listo"})

        #Meto una cadena vacia para que se genere un tercer boton de descarga(el de los informes)
        self.datos_final.append("")
        
        self._csv_final.append({"name": "Resumen.csv", "valor": csv_indi})
        self._csv_final.append({"name": "Especialidades.csv", "valor": csv_espe})

        self.barra = False
        self.mostrar_resultado = True
        self.texto = "Resumen Indicadores:Permite comparar y observar los datos numéricos de manera global de los indicadores de cada año. Concede la capacidad de descargar " \
        "la tabla en formato CSV de los indicadores o de las especialidades de ingreso, además facilita la descarga del Informe Final, el cual incluye todos los datos " \
        "así como los gráficos a elección del facultativo."
        return rx.toast(f"Análisis de los {len(self.nombres_archivos)} documentos completado") if len(self.nombres_archivos) > 1 else rx.toast(f"Análisis del documente completado")

    #Funcion puente que prepara la interfaz para la descarga del informe
    async def preparar_analisis(self):
        grafico=self.ind_grafico
        #1. Mutamos directamente las variables
        self.cerrar_ventana()
        self.ind_grafico=grafico
        self.barra = True
        yield
        
        #2. Mandamos la orden visual a la zona de carga
        yield rx.scroll_to("zona_de_carga")
        
        #3. Obliga al navegador a bajar la pantalla y encender la barra antes de crear el PDF
        await asyncio.sleep(0.5)
        
        #4. Llamamos a la funcion
        yield self.generar_pdf_final()          

    def generar_pdf_final(self):
        #Preparamos el PDF vacio
        pdf = PDF()
        pdf.set_title("Indicadores REA")
        pdf.set_author("Nicolás García Gómez")
        pdf.primera_pagina()
        capitulos = 1

        #Recorremos los calculos almacenados
        for indicador in self._memoria_informe:
            
            #Llamamos al metodo grafico desempaquetando las listas
            grafico_bytes = self.grafico(
                list(indicador["x"]),           
                list(indicador["y"]),           
                indicador["titulo"], 
                indicador["media"], 
                indicador["desviacion"], 
                indicador["error_tipico"], 
                indicador["pend_tendencia"], 
                list(indicador["y_tendencia"]), 
                indicador["r2"]
            )

            #Inyectamos en el PDF todos los datos
            pdf.imp_capitulo(
                capitulos, indicador["titulo"], indicador["subtitulo"], 
                indicador["datos_tabla"], grafico_bytes, 
                indicador["pend_tendencia"], indicador["r2"], 
                ind_especialidades=indicador["es_especialidad"]
            )
            capitulos += 1

        #Añadimos las tablas finales al PDF y descargamos
        pdf.incluir_tabla(self._csv_final[0]["valor"])
        pdf.incluir_tabla(self._csv_final[1]["valor"])
        
        pdf_bytes = bytes(pdf.output(dest="S"))
        
        #Reseteamos el indicador de grafico para que una vez se descargue el informe desaparezca el boton
        self.ind_grafico = ""

        self.barra = False
        
        #Le enviamos el archivo al navegador del usuario
        return rx.download(
            data=pdf_bytes,
            filename="Informe_Indicadores_REA.pdf"
        )

    #Metodo para borrar los datos añadidos
    @rx.event
    def borrar_seleccion(self):
        self.lista_selecc = []
        self.datos_mezcla = []
        self.ind_grafico = ""

    #Metodo que incluye los indicadores seleccionados
    @rx.event
    def seleccion_ind(self, form_data: dict):
        seleccionado = form_data["indicador"]

        #Si la lista no tiene mas de 3 o ya esta añadido lo mete y ejecuta la funcion mezcla
        if  len(self.lista_selecc) < 3 and seleccionado not in self.lista_selecc:
            self.lista_selecc.append(seleccionado)
            return self.mezcla()
        else:
            return rx.window_alert("Solo se permite incluir 3 indicadores sin repetición")
        
    def mezcla(self):
        #Recorre los resultados tras ejecutar cada indicador y añade el valor numerico obtenido
        def recuperar_datos(indicador: str):
            for elem in range(len(self.datos_final)):
                if len(self.datos_mezcla) < len(self.datos_final):
                    self.datos_mezcla.append({"name": self.datos_final[elem]["name"]})
                self.datos_mezcla[elem][indicador] = self.datos_final[elem]["valor"]
        
        #Calcula el maximo real de un indicador en todos los años
        def obtener_maximo_historico(nombre_indicador):
            #Extraemos el valor de ese indicador para cada año(si existe)
            valores = [d.get(nombre_indicador, 0) for d in self.datos_mezcla]
            return max(valores) if valores else 0

        #Diccionario con todos los metodos
        claves = {"Mortalidad Estandarizada":self.mortalidad_estandarizada, "Reingresos no Programados": self.reingresos_no_programados, 
                  "Incidencia de Barotrauma": self.incidencia_de_barotrauma, "Posición Semiincorporada con VMI": self.posicion_semiincorporada_VMI, 
                  "Incidencias Úlcera por Presión UPP": self.incidencia_ulceras_presion,"Interrupción Diaria de la Sedación": self.valoracion_interrupcion_sedacion, 
                  "Prevención Enfermedad Tromboembólica": self.prevencion_enfermedad_tromboembolica, "Mantenimiento de Niveles de Glucemia": self.mantenimiento_niveles_glucemia,
                  "Resucitación Precoz de la Sepsis": self.resucitacion_precoz_sepsis, "Traslado Intrahospitalario": self.traslado_intrahospitalario, 
                  "Tratamiento Empírico Adecuado": self.tratamiento_empirico_infeccion, "Neumonia Asociada a VMI": self.neumonia_asociada_vmi,
                  "Reintubación": self.reintubacion,"Profilaxis de Úlcera por Estrés con NE": self.profilaxis_ulcera_enfermos_NE, 
                  "Sedación Adecuada": self.sedacion_adecuada, "Ingresos Urgentes": self.ingresos_urgentes,
                  "Eventos Adversos Durante el Traslado": self.adversos_traslado, "Nutrición Enteral Precoz": self.ne_precoz, 
                  "Sobretransfusión de Hematíes": self.sobretransfusion_hematies, "TET por Maniobras": self.retirada_accidental, "Bacteriemia relacionada a CVC": self.bacteriemia}
                
        #Limpiamos las variables y activamos el booleano si la lista esta vacia 
        if len(self.lista_selecc) == 0:  
            self.limpieza()
            self.ind_mezcla = True
            self.datos_mezcla = []
        else:
            #Si no esta vacia llamamos al metodo seleccionado y llamamos a la funcion que guarda los datos
            for valor in self.lista_selecc:
                res = claves[valor](ocultar = True)
                res
                if res is not None:
                    self.cerrar_ventana()
                    return res
                recuperar_datos(valor)

        #Ordenamos de MAYOR a MENOR maximo historico:
        #El indicador "más grande" ira PRIMERO en la lista (se dibuja al fondo).
        #El indicador "más pequeño" ira al FINAL de la lista (se dibuja delante).
        self.lista_selecc = sorted(self.lista_selecc, key=obtener_maximo_historico, reverse=True)

        self.datos_final = self.datos_mezcla
        self.mostrar_resultado = True
        self.texto = "Mezcla de Indicadores:Interconecta gráficamente un máximo de tres indicadores permitiendo su comparación directa al mismo tiempo."
        if len(self.lista_selecc) > 1:
            return rx.toast(f"Análisis de los {len(self.lista_selecc)} indicadores completado")
        elif len(self.lista_selecc) == 1:
            return rx.toast(f"Análisis del indicador completado")       