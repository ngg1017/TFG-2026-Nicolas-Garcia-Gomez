import pandas as pd
import tkinter as tk
from tkinter import filedialog

ventada = tk.Tk()
ventada.withdraw()
ventada.attributes('-topmost', True) # Esto asegura que la ventana salga al frente

ruta_seleccionada = filedialog.askopenfilename(
    title = "Selecciona un archivo CSV",
    filetypes = (("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))

if ruta_seleccionada:
    tipo_archivo = ruta_seleccionada.split(".")[1]
    if tipo_archivo != "csv":
        tipo_archivo = None
        print("El archivo solo puede ser del tipo CSV")
    else:
        print("Perfecto, ruta seleccionada correctamente")

else:
    print("Ruta seleccionada incorrectamente")

ventada.destroy()
df_principal = pd.read_csv(ruta_seleccionada, na_values = [""])

def codigo_apache(apache):
    if pd.isna(apache): return 0
    elif apache <= 4: return 0.04
    elif apache <= 9: return 0.08
    elif apache <= 14: return 0.15
    elif apache <= 19: return 0.25
    elif apache <= 24: return 0.40
    elif apache <= 29: return 0.55
    elif apache <= 34: return 0.75
    else: return 0.85

def mortalidad_estandarizada():
    numero_fallecidos = (len(df_principal[df_principal["Fallecido"] == True]))
    df_principal["probabilidad_mortalidad"] = df_principal["Apache"].apply(codigo_apache)
    suma_mortalidad = sum(df_principal["probabilidad_mortalidad"][df_principal["Fallecido"] == True])
    return numero_fallecidos/ suma_mortalidad

def main():
    print(mortalidad_estandarizada())
    
if __name__ == "__main__":
    main()
