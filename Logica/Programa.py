import pandas as pd
import reflex as rx
from .State import State

#Hereda de mi clase State
class Programa(State):
    datos_final: list[dict]
    mostrar_resultado: bool
    texto: str
    
    #Metodo para odeanar los archivos(igual lo pongo en State)
    def ordenar(self):
        pass
    
    #Metodo para parsear los datos aptos para la ventana flotante y los graficos
    def parsear_datos(self, resultado_final):
        self.datos_final = [
            {"name": nombre.split(".")[0][len(nombre)-8:], "valor": round(valor, 4)} 
            for nombre, valor in zip(self.nombres_archivos, resultado_final)
        ]

    #Metodo para cerrar la ventana flotante
    def cerrar_ventana(self):
        self.mostrar_resultado = False

    def codigo_apache(self, apache):
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
        self.datos_final = []
        self.texto = ""
        resultado = []

        #Iteramos sobre las RUTAS temporales
        for ruta in self.rutas_archivos:
            
            #Pandas lee el archivo temporal unico
            df = pd.read_csv(ruta)
            
            #Logica de calculo
            numero_fallecidos = len(df[df["Fallecido"] == True])
            df["probabilidad_mortalidad"] = df["Apache"].apply(self.codigo_apache)
            suma_mortalidad = df.loc[df["Fallecido"] == True, "probabilidad_mortalidad"].sum()
            
            valor_final = (numero_fallecidos / suma_mortalidad) if suma_mortalidad != 0 else 0.0
            resultado.append(float(valor_final))

        self.parsear_datos(resultado)
        self.texto = "La mortalidad estandarizada es una técnica estadística que se utiliza en epidemiología y demografía para comparar las tasas de muerte entre dos poblaciones que tienen estructuras de edad diferentes."
        self.mostrar_resultado = True
        return rx.toast(f"Analisis de los {self.cargados} documentos completado")
    
