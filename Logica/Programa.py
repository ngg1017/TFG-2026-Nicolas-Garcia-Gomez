import pandas as pd
import reflex as rx
from .State import State
import unicodedata

#Hereda de mi clase State
class Programa(State):
    datos_final: list[dict]
    mostrar_resultado: bool
    texto: str

    #Metodo para normalizar las columnas de los dataframes
    def normalizar_frame(self, columna: str):
        columna_unicode = unicodedata.normalize("NFD", columna).encode("ascii", "ignore").decode("utf-8")
        columnas_final = columna_unicode.upper().replace(" ","_").replace(".","_").replace("?","_").replace("/","_").replace(",","_").replace(";","_")
        return columnas_final
    
    #Metodo para parsear los datos aptos para la ventana flotante y los graficos(ordenandolos)
    def parsear_datos(self, resultado_final: list[float]):
        self.datos_final = [
            {"name": nombre.split(".")[0][len(nombre)-8:], "valor": round(valor, 4)} 
            for nombre, valor in zip(self.nombres_archivos, resultado_final)
        ]
        self.datos_final.sort(key= lambda x: x["name"])

    #Metodo para cerrar la ventana flotante
    def cerrar_ventana(self):
        self.mostrar_resultado = False
    
    #Metodo para limpiar todas las variables necesarias e instanciar la lista de resultados
    def limpieza(self):
        self.datos_final = []
        self.texto = ""
        resultado = []
        return resultado

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
        
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")  

        self.parsear_datos(resultado)
        self.texto = "Es un indicador de resultado que mide la calidad y efectividad de un Servicio de Medicina Intensiva (SMI). Su propósito es corregir las limitaciones de la 'mortalidad cruda', la cual no es un buen indicador de calidad porque no tiene en cuenta las diferencias en la gravedad de los pacientes o el tipo de casos atendidos (conocido como case mix)."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {self.cargados} documentos completado")
    
    def reingresos_no_programados(self):
        resultado = self.limpieza()

        try:
            #Iteramos sobre las RUTAS temporales
            for (ruta,nombre) in zip(self.rutas_archivos, self.nombres_archivos):
                
                #Pandas lee el archivo temporal unico
                df = pd.read_csv(ruta)
                #Normalizamos sus columnas
                df.columns = [self.normalizar_frame(col) for col in df.columns]

                if "FECHA_ALTA" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha alta' en {nombre}")
                
                if "FECHA_REINGRESO" not in df.columns:
                    raise ValueError(f"Falta la columna 'Fecha reingreso ' en {nombre}")
                
                #Logica de calculo
                # Conversion a fechas
                df["FECHA_ALTA"] = pd.to_datetime(df["FECHA_ALTA"], format='%d/%m/%Y')
                df["FECHA_REINGRESO"] = pd.to_datetime(df["FECHA_REINGRESO"], format="%d/%m/%Y")

                #Usamos total_seconds() / 3600 para que si pasan 3 dias, nos de 72 horas.
                df["HORAS_DIFERENCIA"] = (df["FECHA_REINGRESO"] - df["FECHA_ALTA"]).dt.total_seconds() / 3600

                # Contar reingresos
                # Filtramos donde la diferencia sea mayor a 48 y sumamos los casos
                numero_reingresos = (df["HORAS_DIFERENCIA"] > 48).sum()

                #Contar altas
                numero_alta = df["FECHA_ALTA"].notna().sum()

                valor_final = (numero_reingresos/numero_alta)*100 if numero_alta != 0 else 0.0
                resultado.append(float(valor_final))
  
        except ValueError as e:
            return rx.window_alert(f"Error crítico: {e}")  

        self.parsear_datos(resultado)
        self.texto = "Es un indicador de resultado que mide la proporción de pacientes que, tras haber sido dados de alta de la UCI a una planta de hospitalización, deben ser reingresados de forma imprevista en la UCI en un periodo de 48 horas."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {self.cargados} documentos completado")
    

