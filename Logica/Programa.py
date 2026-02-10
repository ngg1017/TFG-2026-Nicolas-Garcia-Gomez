import pandas as pd
import reflex as rx
from .State import State
import unicodedata

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

                if "APACHE" not in df.columns:
                    raise ValueError(f"Falta la columna 'Apache' en {nombre}")
                
                if "FALLECIMIENTO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fallecimiento' en {nombre}")
                
                #Logica de calculo
                numero_fallecidos = len(df[df["FALLECIMIENTO"] == True])
                df["PROBABILIDAD_MORTALIDAD"] = df["APACHE"].apply(self.codigo_apache)
                suma_mortalidad = df.loc[df["FALLECIMIENTO"] == True, "PROBABILIDAD_MORTALIDAD"].sum()
                
                valor_final = (numero_fallecidos / suma_mortalidad) if suma_mortalidad != 0 else 0.0
                resultado.append(float(valor_final))

                #Csv que necesita la doctora con los datos filtrados
                data_resumen = {
                    "APACHE": ["RESUMEN GLOBAL mortalidad estandarizada"],
                    "FALLECIMIENTO": [f"Total: {numero_fallecidos}"],
                    "PROBABILIDAD_MORTALIDAD": [f"SMR: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["APACHE","FALLECIMIENTO"], [df["PROBABILIDAD_MORTALIDAD"], df["FALLECIMIENTO"]], 
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

                if "FECHA_ALTA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha alta' en {nombre}")
                
                if "FECHA_REINGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha reingreso' en {nombre}")
                
                #Logica de calculo
                #Conversion a fechas
                df["FECHA_ALTA"] = pd.to_datetime(df["FECHA_ALTA"], format='%d/%m/%Y')
                df["FECHA_REINGRESO"] = pd.to_datetime(df["FECHA_REINGRESO"], format="%d/%m/%Y")

                #Usamos total_seconds() / 3600 para que si pasan 3 dias, nos de 72 horas.
                df["HORAS_DIFERENCIA"] = (df["FECHA_REINGRESO"] - df["FECHA_ALTA"]).dt.total_seconds() / 3600

                #Contar reingresos
                #Filtramos donde la diferencia sea mayor a 48 y sumamos los casos
                numero_reingresos = (df["HORAS_DIFERENCIA"] > 48).sum()

                #Contar altas
                numero_alta = df["FECHA_ALTA"].notna().sum()

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
                    data_resumen, ["BAROTRAUMA","DIAS_VMI"], [df["BAROTRAUMA"], df["DIAS_VMI"]], 
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
        
        #Metodo que hace todas las operaciones finales para ahorrarnos algo de codigo.
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

    #MAL PREGUNTAAR DOCTORAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    def resucitacion_precoz_sepsis(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]

                if "Sepsis" not in df.columns:
                    raise ValueError(f"Falta la columna 'Alta Precoz' en {nombre}")
                
                if "RASS" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha Alta' en {nombre}")
            
                #Logica de calculo
                alta_precoz = df["ALTA_PRECOZ"].fillna(False)
                alta = df["FECHA_ALTA"].notna()
                numero_alta_total = alta.sum()

                #Aquellos que tengan alta precoz y fecha de alta
                num_alta_precoz = (alta & (alta_precoz == True)).sum()

                valor_final = (num_alta_precoz/numero_alta_total)*100 if numero_alta_total != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "ALTA_PRECOZ": ["RESUMEN GLOBAL alta precoz"],
                    "TOTAL_ALTA": [f"Total: {numero_alta_total}"],
                    "TOTAL_ALTA_PRECOZ": [f"Total: {num_alta_precoz}"],
                    "INDICE_ALTA_PRECOZ": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["ALTA_PRECOZ"], [alta_precoz], 
                    f"indicador_alta_precoz_{nombre.split(".")[0][len(nombre)-8:]}.csv"
                )
                
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}") 
        
        self.final(resultado, "Resucitación precoz de la sepsis:")

    def traslado_intrahospitalario(self):
        resultado = self.limpieza()

        try:
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                df = pd.read_csv(ruta)
                df.columns = [self.normalizar_frame(col) for col in df.columns]

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

                if "ANTIBIOTERAPIA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Antibioterapia' en {nombre}")
                
                if "DESESCALADA_ANTIBIOTICA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Desescalada Antibiotica' en {nombre}")
            
                #Logica de calculo
                terapia = df["ANTIBIOTERAPIA"].fillna("Ninguno")
                desescalada = df["DESESCALADA_ANTIBIOTICA"].fillna(False)

                num_infeccion = (terapia != "Ninguno").sum()

                #Aquellos que hagan desescalada y solo tengan un farmaco
                trat_adecuado = ((desescalada == True) & (terapia != "Ninguno") & (~terapia.str.contains(",", na=False))).sum()

                valor_final = (trat_adecuado/num_infeccion)*100 if num_infeccion != 0 else 0.0
                resultado.append(float(valor_final))

                data_resumen = {
                    "ANTIBIOTERAPIA": ["RESUMEN GLOBAL tratamiento empirico"],
                    "DESESCALADA_ANTIBIOTICA": [f"Total: {desescalada.sum()}"],
                    "TOTAL_INFECCIONES": [f"Total: {num_infeccion}"],
                    "TOTAL_TRAT_ADECUADO": [f"Total: {trat_adecuado}"],
                    "INDICE_TRAT_ADECUADO": [f"Total: {float(valor_final)}"]
                }
                self.csv_metodo(
                    data_resumen, ["ANTIBIOTERAPIA", "DESESCALADA_ANTIBIOTICA"], [terapia, desescalada], 
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

    
    
   

        