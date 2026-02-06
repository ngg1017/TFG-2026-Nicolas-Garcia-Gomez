import pandas as pd
import reflex as rx
from .State import State
import unicodedata

"""
Metodo para automatizar el final de cada metodo
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
        columnas_final = columna_unicode.upper().replace(" ","_").replace(".","_").replace("?","_").replace("/","_").replace(",","_").replace(";","_").replace("DE","_")
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

        self.parsear_datos(resultado)
        self.texto = "Mortalidad estandarizada: Es un indicador de resultado que mide la calidad y efectividad de un Servicio de Medicina Intensiva (SMI). Su propósito es corregir las limitaciones de la 'mortalidad cruda'."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado")
    
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

                #Csv que necesita la doctora con los datos filtrados
  
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")  

        self.parsear_datos(resultado)
        self.texto = "Reingresos no programados: Es un indicador de resultado que mide la proporción de pacientes que, tras haber sido dados de alta de la UCI a una planta de hospitalización, deben ser reingresados de forma imprevista en la UCI en un periodo de 48 horas."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado")


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

                numero_barotrauma = df["BAROTRAUMA"].notna().sum()

                dias_barotrauma = (horas_vmi[horas_vmi > 12] / 24).sum()

                valor_final = (numero_barotrauma/dias_barotrauma)*1000 if dias_barotrauma != 0 else 0.0
                resultado.append(float(valor_final))

                #Csv que necesita la doctora con los datos filtrados
  
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")  

        self.parsear_datos(resultado)
        self.texto = "Indice de barotrauma: Es un indicador de seguridad y proceso que mide la aparición de complicaciones pulmonares relacionadas con el daño físico provocado por la ventilación mecánica."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado")    


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
                #MODIFICARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
                #Conversion a horas
                dias_vmi = df["DIAS_VMI"].fillna(0)
                inclinacion = df["GRADOS_INCLINACION"].fillna(0)

                dias_vmi_totales = dias_vmi[dias_vmi > 0].sum()
                total_inclinacion = dias_vmi[(inclinacion > 20) & (dias_vmi > 0)].sum()

                valor_final = (total_inclinacion/dias_vmi_totales)*100 if dias_vmi_totales != 0 else 0.0
                resultado.append(float(valor_final))

                #Csv que necesita la doctora con los datos filtrados
  
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")  

        self.parsear_datos(resultado)
        self.texto = "Posicion semiincorporada con VMI: Es un indicador de proceso que mide el porcentaje de pacientes con ventilación mecánica invasiva que se mantienen con el cabecero de la cama elevado 20º, con el fin de prevenir la neumonía asociada a la ventilación"
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {len(self.rutas_archivos)} documentos completado") if len(self.rutas_archivos) > 1 else rx.toast(f"Analisis del documente completado") 