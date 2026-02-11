import pandas as pd
import reflex as rx
from .State import State
import unicodedata


"""
cambiar metodos numericos por: 
Asegura que son numeros (los errores se vuelven NaN)
rass = pd.to_numeric(df["RASS"], errors="coerce")

Meter strip() en normalizar_frame
"""

#Hereda de mi clase State
class Programa(State):
    datos_final: list[dict]
    csv_final: list[dict]
    mostrar_resultado: bool
    texto: str

    #Metodo para normalizar las columnas de los dataframes
    def normalizar_frame(self, columna: str):
        #Quita los caracteres extraños y las tildes
        columna_unicode = unicodedata.normalize("NFD", columna).encode("ascii", "ignore").decode("utf-8")
        
        #Pasa a mayusculas todo y reemplaza espacios o cualquier otro cararcter de saparacion por "_"
        columnas_final = columna_unicode.upper().replace(" ","_").replace(".","_").replace("?","_").replace("/","_").replace(",","_").replace(";","_").replace("__","_").replace("___","_")
        return columnas_final
    
    #Metodo para parsear los datos aptos para la ventana flotante y los graficos(ordenandolos)
    def parsear_datos(self, resultado_final: list[float]):
        #Creamos el diccionatio dentro de datos_final que se usa en el grafico ordenado por años
        #Ordenamos la lista de diccionarios csv_final por años para que se muestren y descarguen por orden 
        self.datos_final = [
            {"name": nombre.split(".")[0][len(nombre)-8:], "valor": round(valor, 4)} 
            for nombre, valor in zip(self.nombres_archivos, resultado_final)
        ]
        self.datos_final.sort(key= lambda x: x["name"])
        self.csv_final.sort(key= lambda x: x["name"])

    #Metodo para cerrar la ventana flotante
    def cerrar_ventana(self):
        self.mostrar_resultado = False
    
    #Metodo para limpiar todas las variables necesarias e instanciar la lista de resultados
    def limpieza(self):
        self.datos_final = []
        self.texto = ""
        self.csv_final = []
        resultado = []
        return resultado
    
    #Metodo que hace el proceso final de todos los metodos.
    def final(self, datos: list[float], texto: str):
        self.parsear_datos(datos)
        self.texto = texto
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado")
    
    #Metodo que crea el csv que se va a descargar con las columnas y sus transformaciones correspondientes de cada indicador
    def csv_metodo(self,resumen: dict, nombres: list[str], datos: list[pd.DataFrame], nombre_archivo):
        #Creamos el resumen (la fila de arriba)
        df_resumen = pd.DataFrame(resumen)

        #Juntamos las columnas de datos para formar la tabla principal
        #axis=1 para pegar las columnas una al lado de la otra
        df_principal = pd.concat(datos, axis=1)

        #Renombramos las columnas para que coincidan EXACTAMENTE con el resumen
        df_principal.columns = nombres

        #Pegamos el resumen arriba y los datos abajo
        df_final_para_doctora = pd.concat([df_resumen, df_principal], ignore_index=True)
        self.csv_final.append({"name": nombre_archivo, "valor": df_final_para_doctora})
    
    #Metodo que se dispara al presionar el boton de descarga y que basicamente hace lo que indica su nombre
    def descargar_archivo(self, indice: int):
        #Obtenemos el dataFrame y su nombre de la lista de diccionarios
        df = self.csv_final[indice]["valor"]
        nombre = self.csv_final[indice]["name"]
        
        #Lo convertimos a STRING (formato CSV)
        csv_string = df.to_csv( 
            sep=",",         
            index=False,
            encoding="utf-8-sig"
        )
        
        #Disparamos la descarga con nombre y datos correctos
        return rx.download(
            data=csv_string,
            filename=f"{nombre}"
        )

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

    def mortalidad_estandarizada(self):
        resultado = self.limpieza()

        try:
            #Iteramos sobre las RUTAS temporales
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                
                #Pandas lee el archivo temporal unico
                df = pd.read_csv(ruta)
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
                df["PROBABILIDAD_MORTALIDAD"] = df["APACHE"].apply(self.codigo_apache)
                suma_mortalidad = df.loc[fallecimiento == True, "PROBABILIDAD_MORTALIDAD"].sum()
                
                valor_final = (numero_fallecidos / suma_mortalidad)*100 if suma_mortalidad != 0 else 0.0
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
                    f"indicador_mortalidad_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        #Metodo que hace todas las operaciones finales para ahorrarnos algo de codigo.
        self.final(resultado, "Mortalidad estandarizada: Es un indicador de resultado que mide la calidad y efectividad " \
        "de un Servicio de Medicina Intensiva (SMI). " \
        "Su propósito es corregir las limitaciones de la 'mortalidad cruda'.")
        
    def reingresos_no_programados(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "FECHA_ALTA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha alta' en {nombre}")
                
                if "FECHA_REINGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha reingreso' en {nombre}")
                
                #Logica de calculo
                #Conversion a fechas
                df["FECHA_ALTA"] = pd.to_datetime(df["FECHA_ALTA"].fillna(""), format='%d/%m/%Y')
                df["FECHA_REINGRESO"] = pd.to_datetime(df["FECHA_REINGRESO"].fillna(""), format="%d/%m/%Y")

                #Usamos total_seconds() / 3600 para que si pasan 3 dias, nos de 72 horas.
                df["HORAS_DIFERENCIA"] = (df["FECHA_REINGRESO"] - df["FECHA_ALTA"]).dt.total_seconds() / 3600

                #Contar reingresos
                #Filtramos donde la diferencia sea mayor a 48 y sumamos los casos
                numero_reingresos = (df["HORAS_DIFERENCIA"] > 48).sum()

                #Contar altas
                numero_alta = (df["FECHA_ALTA"] != "").sum()

                valor_final = (numero_reingresos/numero_alta)*100 if numero_alta != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "FECHA_ALTA": ["RESUMEN GLOBAL reingresos no programados"],
                    "FECHA_REINGRESO": [f"Total: {numero_reingresos}"],
                    "NUMERO_ALTAS": [f"Total: {numero_alta}"],
                    "REINGRESOS_NO_PROGRAMADOS": [f"SMI: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["FECHA_ALTA","FECHA_REINGRESO"], [df["FECHA_ALTA"], df["FECHA_REINGRESO"]], 
                    f"indicador_reingresos_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Reingresos no programados: Es un indicador de resultado que mide la proporción de pacientes que, " \
        "tras haber sido dados de alta de la UCI a una planta de hospitalización, " \
        "deben ser reingresados de forma imprevista en la UCI en un periodo de 48 horas.")


    def incidencia_de_barotrauma(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "BAROTRAUMA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Barotrauma' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
                
                #Logica de calculo
                #Conversion a horas
                horas_vmi = df["DIAS_VMI"].fillna(0)*24

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
                    data_resumen, ["BAROTRAUMA","DIAS_VMI"], [df["BAROTRAUMA"].fillna(False), df["DIAS_VMI"].fillna("0")], 
                    f"indicador_barotrauma_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Indice de barotrauma: Es un indicador de seguridad y proceso que mide la aparición de complicaciones " \
        "pulmonares relacionadas con el daño físico provocado por la ventilación mecánica.")


    def posicion_semiincorporada_VMI(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "GRADOS_INCLINACION" not in df.columns:
                    raise ValueError(f"Falta la columna 'Grados Inclinacion' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
                
                #Logica de calculo
                dias_vmi = df["DIAS_VMI"].fillna(0)
                inclinacion = df["GRADOS_INCLINACION"].fillna(0)

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
                    f"indicador_posicion_semiincorporada_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Posicion semiincorporada con VMI: Es un indicador de proceso que mide el porcentaje de pacientes " \
        "con ventilación mecánica invasiva que se mantienen con el cabecero de la cama elevado 20º, con el fin de prevenir " \
        "la neumonía asociada a la ventilación")
    
    def incidencia_ulceras_presion(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "UPP" not in df.columns:
                    raise ValueError(f"Falta la columna 'UPP' en {nombre}")
            
                #Logica de calculo
                upp = df["UPP"].fillna(0)

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
                    f"indicador_upp_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Incidencias úlcera por presión UPP: Es un indicador de seguridad que mide el porcentaje " \
        "de pacientes que desarrollan lesiones en la piel o tejidos subyacentes por presión prolongada durante su estancia en " \
        "la UCI, con el objetivo de evaluar la efectividad de las medidas de prevención y cuidados de enfermería")

    def valoracion_interrupcion_sedacion(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "VENTANA_DE_SEDACION" not in df.columns:
                    raise ValueError(f"Falta la columna 'Ventana de sedacion' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
            
                #Logica de calculo
                sedacion = df["VENTANA_DE_SEDACION"].fillna(False)
                dias_vmi = df["DIAS_VMI"].fillna(0)

                #Simplemente que tengan sedacion y dias de vmi necesito otro tipo de datos para hacerlo correctamente
                total_sedacion = dias_vmi[(sedacion == True) & (dias_vmi > 0)].sum()

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
                    data_resumen, ["VENTANA_DE_SEDACION", "DIAS_VMI"], [sedacion, dias_vmi], 
                    f"indicador_sedacion_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Interrupción de la sedación: Es un indicador de proceso que mide el porcentaje " \
        "de días en los que se evalúa y ejecuta la suspensión diaria de la sedación continua en pacientes con ventilación mecánica, " \
        "con el fin de reducir la duración del soporte ventilatorio y la estancia en la UCI. " \
        "Debido a la estructura de la base de datos, " \
        "donde la interrupción de la sedación se registra como una variable dicotómica (Sí/No) por paciente y no de forma diaria, el indicador " \
        "se ha calculado asumiendo que el cumplimiento del protocolo se extiende a la totalidad de los días de ventilación " \
        "mecánica del paciente registrado.")
    
    def prevencion_enfermedad_tromboembolica(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
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
                    f"indicador_tvp_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Prevención enfermedad tromboembólica: Es un indicador de proceso que mide el porcentaje de pacientes " \
        "que reciben profilaxis antitrombótica adecuada (farmacológica o mecánica), " \
        "con el fin de evitar complicaciones graves como la trombosis venosa profunda o el tromboembolismo pulmonar.")

    def mantenimiento_niveles_glucemia(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "GLUCEMIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Glucemia' en {nombre}")
                
                if "TRATAMIENTO_INSULINA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Tratamiento insulina' en {nombre}")
            
                #Logica de calculo
                glucemia = df["GLUCEMIA"].fillna(0)
                insulina = df["TRATAMIENTO_INSULINA"].fillna(False)

                #Aquellos que tengas insulina y glucemia > 150 a la vez
                total = insulina[(glucemia >= 150) & (insulina == True)].sum()
                total_glucemia = (glucemia >= 150).sum()

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
                    f"indicador_glucemia_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Mantenimiento de niveles de glucemia: Es un indicador de proceso que mide el porcentaje de pacientes en " \
        "los que se mantiene una glucemia capilar de 150, con el fin de evitar tanto la hiperglucemia como la hipoglucemia " \
        "grave y reducir así la morbi-mortalidad asociada.")

    def resucitacion_precoz_sepsis(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
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
                pam_ingreso = df["PAM_INGRESO"].fillna(0)
                pam_6 = df["PAM_6H"].fillna(0)
                pam_24 = df["PAM_24H"].fillna(0)
                diuresis_ingreso = df["DIURESIS_INGRESO"].fillna(0)
                diuresis_6 = df["DIURESIS_6H"].fillna(0)
                diuresis_24 = df["DIURESIS_24H"].fillna(0)
                lactato_ingreso = df["LACTATO_INGRESO"].fillna(0)
                lactato_6 = df["LACTATO_6H"].fillna(0)
                lactato_24 = df["LACTATO_24H"].fillna(0)
                alta = df["FECHA_ALTA"].fillna("")
            
                #Calculamos la resucitacion con la PAM, Diuresis y el Lactato mayores a un numero o cambio del 50% en lactato
                resucitacion_ingreso = ((pam_ingreso > 65)&(diuresis_ingreso > 0.5)&((lactato_ingreso > 0.9) & (lactato_ingreso < 1.1)))
                resucitacion_6 = ((pam_6 > 65)&(diuresis_6 > 0.5)&(((lactato_6 > 0.9) & (lactato_6 < 1.1))|((lactato_ingreso*0.5) >= lactato_6)))
                resucitacion_24 = ((pam_24 > 65)&(diuresis_24 > 0.5)&(((lactato_24 > 0.9) & (lactato_24 < 1.1))|((lactato_6*0.5) >= lactato_24)))

                #Donde tengan sepsis, SS y se de la resucitacion precoz
                numerador = ((sepsis|ss)&(resucitacion_ingreso|resucitacion_6|resucitacion_24)).sum()

                #Enfermos que tengan sepsis, SS y esten dados de alta
                denominador = ((sepsis|ss)&(alta != "")).sum()

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
                    "FECHA_ALTA": [f"Total: {(alta != "").sum()}"]
                }
                self.csv_metodo(
                    data_resumen, ["SEPSIS","SHOCK_SEPTICO","PAM_INGRESO","PAM_6H","PAM_24H","DIURESIS_INGRESO","DIURESIS_6H",
                                   "DIURESIS_24H","LACTATO_INGRESO","LACTATO_6H","LACTATO_24H","LACTATO_VARIACION_6",
                                   "LACTATO_VARIACION_24","FECHA_ALTA"], 
                    [sepsis,ss,pam_ingreso,pam_6,pam_24,diuresis_ingreso,diuresis_6,
                     diuresis_24,lactato_ingreso,lactato_6,lactato_24,
                     lactato_ingreso.astype(str) + " - " + lactato_6.astype(str),lactato_6.astype(str) + " - " + lactato_24.astype(str),alta], 
                    f"indicador_resucitacion_precoz_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Resucitación precoz de la sepsis: Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con sepsis o shock séptico que reciben el paquete de medidas de tratamiento inicial (administración de fluidos y " \
        "vasopresores) en los plazos establecidos, con el fin de restaurar la perfusión tisular y reducir la mortalidad.")

    def traslado_intrahospitalario(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
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
                    f"indicador_listado_traslado_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Traslado intrahospitalario: Es un indicador de proceso que mide el porcentaje de traslados de pacientes " \
        "críticos fuera de la UCI (a pruebas de imagen o quirófano) realizados utilizando un listado de verificación (check-list) " \
        "estandarizado, con el fin de minimizar los eventos adversos y garantizar la seguridad durante el transporte.")

    def tratamiento_empirico_infeccion(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "ANTIBIOTERAPIA_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Antibioterapia Ingreso' en {nombre}")
                
                if "ANTIBIOTERAPIA_24H" not in df.columns:
                    raise ValueError(f"Falta la columna 'Antibioterapia 24h' en {nombre}")
                
                if "DESESCALADA_ANTIBIOTICA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Desescalada Antibiotica' en {nombre}")
            
                #Logica de calculo
                terapia_in = df["ANTIBIOTERAPIA_INGRESO"].fillna("Ninguno")
                terapia_fin = df["ANTIBIOTERAPIA_24H"].fillna("Ninguno")
                desescalada = df["DESESCALADA_ANTIBIOTICA"].fillna(False)

                #Aquellos que tenga terapia
                num_infeccion = ((terapia_in != "Ninguno")&(terapia_fin != "Ninguno")).sum()

                def verificar_coincidencia(row):
                    #"Ninguno" no es coincidencia válida
                    if row['in'] == "Ninguno" or row['fin'] == "Ninguno":
                        return False
                    
                    #Convertimos los strings en listas
                    lista_in = [x.strip() for x in row['in'].split(',')]
                    lista_fin = [x.strip() for x in row['fin'].split(',')]
                    
                    #Comprobamos si hay algun elemento comun
                    return any(farmaco in lista_fin for farmaco in lista_in)

                #Creamos un DataFrame temporal para el apply
                df_temp = pd.DataFrame({'in': terapia_in, 'fin': terapia_fin})
                trat = df_temp.apply(verificar_coincidencia, axis=1)
                #Aquellos que hagan desescalada y coincidan sus farmacos
                trat_adecuado = (desescalada & (terapia_in != "Ninguno") & (terapia_fin != "Ninguno") & trat).sum()
                    
                valor_final = (trat_adecuado/num_infeccion)*100 if num_infeccion != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "TRATAMIENTO_ADECUADO": ["RESUMEN GLOBAL tratamiento empirico"],
                    "ANTIBIOTERAPIA_INGRESO": [f"Total: {(terapia_in != "Ninguno").sum()}"],
                    "ANTIBIOTERAPIA_24H": [f"Total: {(terapia_fin != "Ninguno").sum()}"],
                    "DESESCALADA_ANTIBIOTICA": [f"Total: {desescalada.sum()}"],
                    "TOTAL_INFECCIONES": [f"Total: {num_infeccion}"],
                    "TOTAL_TRAT_ADECUADO": [f"Total: {trat_adecuado}"],
                    "INDICE_TRAT_ADECUADO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["ANTIBIOTERAPIA_INGRESO","ANTIBIOTERAPIA_24H", "DESESCALADA_ANTIBIOTICA"], 
                    [terapia_in, terapia_fin, desescalada], 
                    f"indicador_trat_adecuado_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Tratamiento empírico adecuado: Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con sospecha de infección grave que reciben una terapia antibiótica inicial ajustada a las guías clínicas y a los " \
        "mapas de resistencias locales en menos de una hora, con el fin de reducir drásticamente la mortalidad y la disfunción orgánica")

    def neumonia_asociada_vmi(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "EPISODIOS_NAV" not in df.columns:
                    raise ValueError(f"Falta la columna 'Episodios NAV' en {nombre}")
                
                if "DIAS_VMI" not in df.columns:
                    raise ValueError(f"Falta la columna 'Dias VMI' en {nombre}")
            
                #Logica de calculo
                nav = df["EPISODIOS_NAV"].fillna(0)
                vmi = df["DIAS_VMI"].fillna(0)

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
                    data_resumen, ["EPISODIOS_NAV", "DIAS_VMI"], [nav, vmi], 
                    f"indicador_nav_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Neumonia asociada a VMI: Es un indicador de seguridad que mide el número de episodios " \
        "de neumonía desarrollados por cada 1.000 días de ventilación mecánica, con el " \
        "fin de evaluar la eficacia de las medidas preventivas y reducir las complicaciones infecciosas del paciente crítico")

    def reintubacion(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "REGISTRO_INTUBACIONES" not in df.columns:
                    raise ValueError(f"Falta la columna 'Registro Intubaciones' en {nombre}")
                
                if "EXTUBACION_PROGRAMADA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Extubacion Programada' en {nombre}")
            
                #Logica de calculo
                intuba = df["REGISTRO_INTUBACIONES"].fillna("")
                extuba = df["EXTUBACION_PROGRAMADA"].fillna(False)

                #Aquellos que contengan mas de un registro en intubaciones
                reintubaciones = (intuba.str.contains(",", na=False)).sum()
                num_extuba = ((intuba != "")&(extuba == True)).sum()

                valor_final = (reintubaciones/num_extuba)*100 if num_extuba != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "REGISTRO_INTUBACIONES": ["RESUMEN GLOBAL nuemonia asociada a VMI"],
                    "EXTUBACION_PROGRAMADA": [f"Total: {num_extuba}"],
                    "TOTAL_INTUBACIONES": [f"Total: {(intuba != "").sum()}"],
                    "TOTAL_REINTUBACIONES": [f"Total: {reintubaciones}"],
                    "INDICE_REINTUBACIONES": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["REGISTRO_INTUBACIONES", "EXTUBACION_PROGRAMADA"], [intuba, extuba], 
                    f"indicador_reintubaciones_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Reintubación: Es un indicador de resultado que mide el porcentaje de pacientes que requieren " \
        "la inserción de un tubo endotraqueal posterior a una extubación planificada, con el objetivo de evaluar " \
        "el éxito del destete y evitar el aumento de la morbimortalidad asociada al fracaso de la extubación.")
    
    def especialidad_ingreso(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "ESPECIALIDAD_DE_INGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Especialidad de ingreso' en {nombre}")
            
                #Logica de calculo
                especialidad = df["ESPECIALIDAD_DE_INGRESO"].fillna("No especificada")
                valores = especialidad.value_counts(normalize=True)

                #Me salto el metodo de parsear los datos pero se muestran en el grafico mal
                for (nomb,valor) in zip (valores.index, valores.values):
                    self.datos_final.append({"name": nomb, "valor": valor * 100})
                
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
                    f"indicador_especialidad_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        #Me salto el metodo final ya que hay variaciones en los datos
        #Tengo que modificarlo de tal forma que me muestre las especialidades por año descaargandome solo por años
        self.datos_final.sort(key= lambda x: x["name"])
        self.csv_final.sort(key= lambda x: x["name"])
        self.texto = "Especialidad con mayor ingreso:"
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado")

    def profilaxis_ulcera_enfermos_NE(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
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
                    raise ValueError(f"Falta la columna 'Fecha Inicio NE en {nombre}")
                
                if "PROFILAXIS_TVP" not in df.columns:
                    raise ValueError(f"Falta la columna 'Profilaxis TVP' en {nombre}")
                        
                #Logica de calculo
                corticoides = df["TRATAMIENTO_CORTICOIDES"].fillna(False)
                hemorragia = df["ANTECEDENTES_HEMORRAGIA_GI"].fillna(False)
                coagulopatia = df["COAGULOPATIA"].fillna(False)
                renal = df["INSUFICIENCIA_RENAL"].fillna(False)
                hepatica = df["INSUFICIENCIA_HEPATICA"].fillna(False)
                ne = df["FECHA_INICIO_NE"].fillna("")
                profilaxis = df["PROFILAXIS_TVP"].fillna(False)

                #Calculamos la hgi que tiene los siguiente componentes
                hgi = ((corticoides == True)|(hemorragia == True)|(coagulopatia == True)|(renal == True)|(hepatica == True))
                #Donde haya HGI, nutricion enteral y no haya profilaxis
                ne_profilaxis_hgi = ((hgi == True)&(ne != "")&(profilaxis == False)).sum()
                #Donde haya HGI y nutricion enteral
                ne_hgi = ((hgi == True)&(ne != "")).sum()

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
                    "FECHA_INICIO_NE": [f"Total: {(ne != "").sum()}"],
                    "PROFILAXIS_TVP": [f"Total: {profilaxis.sum()}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["CORTICOIDES", "ANTECEDENTES_HEMORRAGIA_GI", "COAGULOPATIA", 
                                   "INSUFICIENCIA_RENAL", "INSUFICIENCIA_HEPATICA", "FECHA_INICIO_NE", "PROFILAXIS_TVP"], 
                                  [corticoides, hemorragia, coagulopatia, renal, hepatica, ne, profilaxis], 
                    f"indicador_profilaxis_ulceras_NE_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Profilaxis de ulcera por estrés con NE: Es un indicador de proceso que mide el porcentaje de " \
        "pacientes con nutrición enteral que no reciben fármacos supresores del ácido gástrico innecesariamente, con el fin de " \
        "evitar efectos adversos, ya que la propia nutrición se considera protectora.")

    def sedacion_adecuada(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]
                if df.columns.duplicated().any():
                    df = df.loc[:, ~df.columns.duplicated()]

                if "RASS" not in df.columns:
                    raise ValueError(f"Falta la columna 'RASS' en {nombre}")
                
                if "BIS" not in df.columns:
                    raise ValueError(f"Falta la columna 'BIS' en {nombre}")
                
                #Logica de calculo
                rass = pd.to_numeric(df["RASS"], errors="coerce")
                bis = pd.to_numeric(df["BIS"], errors="coerce")

                #Sedacion ligera -2 <= rass <= 0
                sedacion_ligera = ((rass >= -2)&(rass <= 0))
                #Sedacion profunda -5 < rass <= -4
                sedacion_profunda = ((rass > -5) & (rass <= -4))
                #Sedacion paralizado rass == -5 y 40 <= bis <= 60 o la bis sea nula que se acepta tambien como sedacion
                sedacion_paralizado = (rass == -5) & (((bis >= 40) & (bis <= 60)) | bis.isna())

                #Sedacion adecuada
                sedacion_adecuada = (sedacion_ligera|sedacion_profunda|sedacion_paralizado).sum()
                #Total sedacion
                sedacion = ((rass.notna())|(bis.notna())).sum()

                valor_final = (sedacion_adecuada/sedacion)*100 if sedacion != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "SEDACION_ADECUADA": ["RESUMEN GLOBAL profilaxis de ulcera con NE"],
                    "RASS_LIGERA": [f"Total: {sedacion_ligera.sum()}"],
                    "RASS_PROFUNDA": [f"Total: {sedacion_profunda.sum()}"],
                    "RASS_PARALIZADO": [f"Total: {sedacion_paralizado.sum()}"],
                    "BIS_PARALIZADO": [f"Total: {sedacion_paralizado.sum()}"],
                    "SEDACION_ADECUADA": [f"Total: {sedacion_adecuada}"],
                    "TOTAL_SEDACION": [f"Total: {sedacion}"],
                    "INDICADOR_FINAL": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["RASS", "BIS","RASS_LIGERA","RASS_PROFUNDA","RASS_PARALIZADO","BIS_PARALIZADO"], 
                    [rass,bis,rass[sedacion_ligera],rass[sedacion_profunda], rass[sedacion_paralizado],bis[sedacion_paralizado]], 
                    f"indicador_sedacion_adecuada_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Sedación adecuada: Sedación adecuada es el mantenimiento de " \
        "los resultados de las escalas de sedación dentro del rango prescrito (objetivo) para ese enfermo en particular.")
    
    
   

        