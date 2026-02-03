import pandas as pd
import reflex as rx
from Logica.State import State

class Programa(State):
    resultado_mortalidad: list = []

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
        for file in self.documentos:
            df = pd.DataFrame(file)
            numero_fallecidos = (len(df[df["Fallecido"] == True]))
            df["probabilidad_mortalidad"] = df["Apache"].apply(self.codigo_apache)
            suma_mortalidad = sum(df["probabilidad_mortalidad"][df["Fallecido"] == True])
            self.resultado_mortalidad.append(numero_fallecidos / suma_mortalidad)
        return rx.toast(f"Cálculo finalizado {self.resultado_mortalidad}")
