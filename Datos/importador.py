import pandas as pd
import glob
from sqlalchemy import create_engine, text
import unicodedata # NUEVO: Para quitar tildes

#Establece la conexion antigua
#engine = create_engine("postgresql://postgres:postgres@localhost:5432/tfg_bbdd")

#Apunta a tu base de datos de Docker
engine = create_engine("postgresql://medico:secreto123@localhost:5433/hospital_db")

#Limpia la tabla
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE registro RESTART IDENTITY;"))
print("Tabla 'registro' vaciada correctamente...")

archivos_csv = glob.glob("Datos*.csv")

mapeo_columnas = {
    "Fecha Ingreso": "fecha_ingreso", "Reingreso 48": "reingreso_48", "Fecha Alta": "fecha_alta",
    "Barotrauma": "barotrauma", "VMI": "vmi", "Dias VMI": "dias_vmi", "Grados Inclinacion": "grados_inclinacion",
    "UPP": "upp", "Ventana de Sedacion": "ventana_sedacion", "Profilaxis TVP": "profilaxis_tvp",
    "TVP": "tvp", "Glucemia": "glucemia", "Tratamiento Insulina": "tratamiento_insulina",
    "Sepsis": "sepsis", "Shock Septico": "shock_septico", "Traslado Intrahospitalario": "traslado_intrahospitalario",
    "Tratamiento adecuado": "tratamiento_adecuado", "Cobertura empirica completa": "cobertura_empirica_completa",
    "Resistencia antibioticos": "resistencia_antibioticos", "Fallecimiento": "fallecimiento",
    "APACHE": "apache", "Tratamiento Corticoides": "tratamiento_corticoides",
    "Antecedentes Hemorragia GI": "antecedentes_hemorragia_gi", "Coagulopatia": "coagulopatia",
    "Insuficiencia Renal": "insuficiencia_renal", "Insuficiencia Hepatica": "insuficiencia_hepatica",
    "Episodios NAV": "episodios_nav", "Registro Intubaciones": "registro_intubaciones",
    "Extubacion Programada": "extubacion_programada", "Especialidad de Ingreso": "especialidad_ingreso",
    "Ingreso por Urgencia": "ingreso_urgencia", "Eventos Adversos Traslado": "eventos_adversos_traslado",
    "Fecha Inicio NE": "fecha_inicio_ne", "Omeprazol": "omeprazol", "Actos Transfusionales": "actos_transfusionales",
    "Cantidad_transfusion_dia": "cantidad_transfusion_dia", "Sangrado Activo": "sangrado_activo",
    "Extubacion por Maniobras": "extubacion_maniobras", "Listado de Verificacion": "listado_verificacion",
    "PAM_ingreso": "pam_ingreso", "PAM_6h": "pam_6h", "PAM_24h": "pam_24h",
    "Diuresis_ingreso": "diuresis_ingreso", "Diuresis_6h": "diuresis_6h", "Diuresis_24h": "diuresis_24h",
    "Lactato_ingreso": "lactato_ingreso", "Lactato_6h": "lactato_6h", "Lactato_24h": "lactato_24h",
    "BIS objetivo": "bis_objetivo", "RASS objetivo": "rass_objetivo", "RASS": "rass", "BIS": "bis",
    "Numero Episodios Bacteriemia": "numero_episodios_bacteriemia", "Numero total de dias CVC": "numero_total_dias_cvc"
}

orden_db = [
    "num_historia", "fecha_ingreso", "fecha_alta", "reingreso_48", "especialidad_ingreso", "ingreso_urgencia", "fallecimiento", "apache",
    "vmi", "dias_vmi", "barotrauma", "grados_inclinacion", "episodios_nav", "registro_intubaciones", "extubacion_programada", "extubacion_maniobras",
    "sepsis", "shock_septico", "pam_ingreso", "pam_6h", "pam_24h", "diuresis_ingreso", "diuresis_6h", "diuresis_24h", "lactato_ingreso", "lactato_6h", "lactato_24h",
    "tratamiento_adecuado", "cobertura_empirica_completa", "resistencia_antibioticos", "numero_episodios_bacteriemia", "numero_total_dias_cvc",
    "rass", "bis", "rass_objetivo", "bis_objetivo", "ventana_sedacion",
    "fecha_inicio_ne", "omeprazol", "tratamiento_corticoides", "antecedentes_hemorragia_gi", "coagulopatia", "insuficiencia_renal", "insuficiencia_hepatica",
    "upp", "profilaxis_tvp", "tvp", "glucemia", "tratamiento_insulina", "traslado_intrahospitalario", "listado_verificacion", "eventos_adversos_traslado", "actos_transfusionales", "sangrado_activo", "cantidad_transfusion_dia"
]

for archivo in archivos_csv:
    print(f"Procesando {archivo}...")
    
    #Leemos el archivo. Si utf-8 falla, usamos latin1.
    try:
        df = pd.read_csv(archivo, sep=",", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(archivo, sep=",", dtype=str, encoding="latin1")
    
    df.rename(columns=mapeo_columnas, inplace=True)
    
    año = archivo.replace("Datos", "").replace(".csv", "")
    df.insert(0, "num_historia", [f"H-{año}-{i+1}" for i in range(len(df))])
    df = df[orden_db]

    #Limpiamos las especialidades para que entren impecables a la base de datos
    if "especialidad_ingreso" in df.columns:
        df["especialidad_ingreso"] = df["especialidad_ingreso"].fillna("")
        
        def limpiar_texto(texto):
            #Si esta vacio o es un nulo de Pandas, devuelve None
            if not texto or pd.isna(texto): 
                return None
                
            t = str(texto)
            
            #Reemplazos blindados (sin copiar simbolos raros)
            t = t.replace("ï¿½", "i")
            #\ufffd es el codigo seguro e invisible del rombo negro
            t = t.replace("\ufffd", "i") 
            
            #Quitar tildes que hayan sobrevivido
            sin_tildes = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
            
            #Poner en formato Título y limpiar espacios extra
            return sin_tildes.title().strip()

        df["especialidad_ingreso"] = df["especialidad_ingreso"].apply(limpiar_texto)

    #Limpia casillas vacias (espacios) y NaNs para convertirlos a None (NULL de SQL)
    df = df.replace(r"^\s*$", None, regex=True)
    df = df.where(pd.notnull(df), None)
    
    df.to_sql("registro", engine, if_exists="append", index=False)

print("¡Importacion finalizada con exito total!")