import pandas as pd
import reflex as rx
from .State import State

class Programa(State):
    resultado_mortalidad: list[float]

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
    
    def ordenar(self):
        pass

    def mortalidad_estandarizada(self):
        self.resultado_mortalidad = []

        #Iteramos sobre las RUTAS temporales
        for ruta in self.rutas_archivos:
            
            # Pandas lee el archivo temporal unico
            df = pd.read_csv(ruta)
            
            #Logica de calculo
            numero_fallecidos = len(df[df["Fallecido"] == True])
            df["probabilidad_mortalidad"] = df["Apache"].apply(self.codigo_apache)
            suma_mortalidad = df.loc[df["Fallecido"] == True, "probabilidad_mortalidad"].sum()
            
            valor_final = (numero_fallecidos / suma_mortalidad) if suma_mortalidad != 0 else 0.0
            self.resultado_mortalidad.append(float(valor_final))

        return rx.toast(f"Cálculo finalizado {self.resultado_mortalidad}")
