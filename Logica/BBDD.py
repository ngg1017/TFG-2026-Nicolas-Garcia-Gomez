import reflex as rx
import pandas as pd
import tempfile
import os
from Logica.State import State 

class BBDD(rx.State):
    #Variable que controla si el panel de la tabla es visible o no
    viendo_consulta: bool = False
    #Lista que almacena temporalmente los años que el usuario selecciona
    años_seleccionados: list[str] = []
    
    #Lista principal con los nombres completos necesarios para los calculos internos
    cabeceras: list[str] = [
        "Num Historia", "Fecha Ingreso", "Fecha Alta", "Reingreso 48", "Especialidad de ingreso", "Ingreso por Urgencia", "Fallecimiento", "APACHE",
        "VMI", "Días VMI", "Barotrauma", "Grados Inclinación", "Episodios NAV", "Registro Intubaciones", "Extubación Programada", "Extubación por Maniobras",
        "Sepsis", "Shock Séptico", "PAM ingreso", "PAM 6h", "PAM 24h", "Diuresis Ingreso", "Diuresis 6h", "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", "Lactato 24h",
        "Tratamiento adecuado", "Cobertura empírica completa", "Resistencia antibióticos", "Número Episodios Bacteriemia", "Número total de días CVC",
        "RASS", "BIS", "RASS objetivo", "BIS objetivo", "Ventana de sedación",
        "Fecha Inicio NE", "Omeprazol", "Tratamiento Corticoides", "Antecedentes Hemorragia GI", "Coagulopatía", "Insuficiencia Renal", "Insuficiencia Hepática",
        "UPP", "Profilaxis TVP", "TVP", "Glucemia", "Tratamiento insulina", "Traslado Intrahospitalario", "Listado de verificación", "Eventos Adversos Traslado", "Actos Transfusionales", "Sangrado Activo", "Cantidad Transfusión Dia"
    ]

    #Lista secundaria con abreviaturas legibles exclusivamente para la interfaz grafica
    cabeceras_display: list[str] = [
        "Nº Historia", "Fecha Ingreso", "Fecha Alta", "Reingreso 48h", "Especialidad", "Ingreso Urgencia", "Fallecimiento", "APACHE",
        "VMI", "Días VMI", "Barotrauma", "Grados Inclinación", "Episodios NAV", "Registro Intubación", "Extub. Programada", "Extub. Maniobras",
        "Sepsis", "Shock Séptico", "PAM Ingreso", "PAM 6h", "PAM 24h", "Diuresis Ingreso", "Diuresis 6h", "Diuresis 24h", "Lactato Ingreso", "Lactato 6h", "Lactato 24h",
        "Trat. Adecuado", "Cobertura Empírica", "Resist. Antibióticos", "Bacteriemia", "Días CVC",
        "RASS", "BIS", "RASS Objetivo", "BIS Objetivo", "Ventana Sedación",
        "Fecha Inicio NE", "Omeprazol", "Trat. Corticoides", "Hemorragia GI", "Coagulopatía", "Insuf. Renal", "Insuf. Hepática",
        "UPP", "Profilaxis TVP", "TVP", "Glucemia", "Trat. Insulina", "Traslado Intra.", "Listado Verific.", "Eventos Traslado", "Transfusiones", "Sangrado Activo", "Cant. Transfusiones"
    ]

    #Matriz bidimensional que contiene todos los registros historicos de los pacientes
    datos_mostrados: list[list[str]] = [
        #Rellena el resto de las cincuenta y cinco columnas con ceros para cuadrar el dataframe
        ["H-2026-001", "10/01/2026", "25/01/2026", "False", "Cardiología", "True", "False", "18"] + ["0"] * 47,
        ["H-2025-045", "15/12/2025", "05/01/2026", "False", "Digestivo", "False", "False", "9"] + ["0"] * 47,
        ["H-2024-112", "20/05/2024", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-11", "20/05/2023", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-1", "20/05/2022", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2021", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2020", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2019", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2018", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2017", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2016", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2026-001", "10/01/2026", "25/01/2026", "False", "Cardiología", "True", "False", "18"] + ["0"] * 47,
        ["H-2025-045", "15/12/2025", "05/01/2026", "False", "Digestivo", "False", "False", "9"] + ["0"] * 47,
        ["H-2024-112", "20/05/2024", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-11", "20/05/2023", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-1", "20/05/2022", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2021", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2020", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2019", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2018", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2017", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2016", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2026-001", "10/01/2026", "25/01/2026", "False", "Cardiología", "True", "False", "18"] + ["0"] * 47,
        ["H-2025-045", "15/12/2025", "05/01/2026", "False", "Digestivo", "False", "False", "9"] + ["0"] * 47,
        ["H-2024-112", "20/05/2024", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-11", "20/05/2023", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-1", "20/05/2022", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2021", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2020", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2019", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2018", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2017", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2016", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2026-001", "10/01/2026", "25/01/2026", "False", "Cardiología", "True", "False", "18"] + ["0"] * 47,
        ["H-2025-045", "15/12/2025", "05/01/2026", "False", "Digestivo", "False", "False", "9"] + ["0"] * 47,
        ["H-2024-112", "20/05/2024", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-11", "20/05/2023", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-1", "20/05/2022", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2021", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2020", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2019", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2018", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2017", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
        ["H-2024-112", "20/05/2016", "30/05/2024", "True", "Neumología", "True", "True", "25"] + ["0"] * 47,
    ]

    #Decorador que indica a reflex que esta variable se calcula dinamicamente
    @rx.var
    #Funcion que extrae todos los años disponibles sin repeticiones
    def años_disponibles(self) -> list[str]:
        años = set()

        #Itera sobre cada paciente dentro de los datos
        for fila in self.datos_mostrados:
            #Extrae el indice uno correspondiente a la fecha de ingreso
            fecha_ingreso = fila[1] 
            #Comprueba que la variable fecha no este vacia
            if fecha_ingreso:
                año = fecha_ingreso.split("/")[-1] 
                años.add(año)

        #Retorna la lista final convertida y ordenada de forma descendente
        return sorted(list(años), reverse=True)

    #Funcion que gestiona la logica de marcado y desmarcado de los botones de años
    def toggle_año(self, año: str):
        #Verifica si el año pulsado ya se encontraba previamente en la lista
        if año in self.años_seleccionados:
            #Reasigna la lista completa excluyendo el año para forzar la actualizacion visual
            self.años_seleccionados = [a for a in self.años_seleccionados if a != año]

        #Ejecuta el bloque secundario en caso de que el año no estuviera seleccionado
        else:
            #Comprueba que no se haya superado el limite de seguridad de diez archivos
            if len(self.años_seleccionados) < 10:
                #Reasigna la lista añadiendo el nuevo año mediante suma de listas
                self.años_seleccionados = self.años_seleccionados + [año]
            #Bloque que se ejecuta si el usuario intenta superar el limite establecido
            else:
                return rx.toast("Has alcanzado el máximo de 10 años")

    #Funcion asincrona responsable de filtrar y exportar los datos al analizador
    async def enviar_a_analisis(self):
        #Verifica que haya al menos una seleccion activa antes de procesar
        if len(self.años_seleccionados) == 0:
            return rx.toast("Seleccione al menos un año")

        #Pausa la ejecucion para extraer las variables del estado principal
        estado_principal = await self.get_state(State)
        archivos_creados = 0

        #Itera individualmente sobre cada año que el usuario haya seleccionado
        for año in self.años_seleccionados:
            #Crea una lista por comprension que solo guarda las filas terminadas en el año actual
            datos_filtrados = [fila for fila in self.datos_mostrados if str(fila[1]).endswith(año)]

            #Comprueba si el filtrado no ha devuelto resultados para evitar errores
            if len(datos_filtrados) == 0:
                #Salta directamente al siguiente ciclo del bucle si no hay pacientes
                continue

            #Genera el dataframe utilizando la lista de cabeceras largas originales
            df = pd.DataFrame(datos_filtrados, columns=self.cabeceras)

            #Abre un flujo seguro para crear el archivo temporal en el disco duro
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='latin1', newline='') as tmp:
                #Vuelca el dataframe completo transformandolo en formato csv
                df.to_csv(tmp, sep=',', index=False)
                #Captura la ruta fisica donde el sistema operativo guardo el archivo
                ruta_tmp = tmp.name

            #Genera un nombre estetico que vera el usuario en el historial
            nombre_ficticio = f"BBDD_Historico_{año}.csv"

            #Bucle de seguridad para mantener limpia la memoria eliminando archivos antiguos
            while len(estado_principal.rutas_archivos) >= 10:
                #Extrae y elimina la ruta mas antigua de la primera posicion de la cola
                ruta_a_borrar = estado_principal.rutas_archivos.pop(0)
                #Extrae el nombre asociado de la lista paralela
                nombre_a_borrar = estado_principal.nombres_archivos.pop(0)
                #Guarda el nombre en el historial de archivos borrados
                estado_principal.nombres_archivos_eliminados.append(nombre_a_borrar)
                #Comprueba si la ruta sigue existiendo fisicamente en el disco
                if os.path.exists(ruta_a_borrar):
                    #Ordena al sistema operativo la destruccion del archivo
                    os.remove(ruta_a_borrar)

            #Inyecta la nueva ruta generada en la logica global de la aplicacion
            estado_principal.rutas_archivos.append(ruta_tmp)
            #Inyecta el nombre estetico correspondiente en el estado principal
            estado_principal.nombres_archivos.append(nombre_ficticio)
            #Suma un digito al contador global de exito por cada iteracion completada
            archivos_creados += 1

        #Actualiza la estadistica general de archivos analizados por la plataforma
        estado_principal.cargados += archivos_creados
        #Vacia la lista de seleccion para reiniciar el componente visual
        self.años_seleccionados = [] 
        #Cambia el booleano para cerrar automaticamente la ventana tras el volcado
        self.viendo_consulta = False
        
        #Muestra el aviso final detallando cuantos años fueron extraidos correctamente
        return rx.toast(f"Registros de {archivos_creados} años cargados. Haciendo un total de {estado_principal.cargados} archivos procesados.")
    
    #Metodos que cambia el estado booleano para desplegar/cerrar la ventana
    def abrir_consulta(self):
        self.viendo_consulta = True

    def cerrar_consulta(self):
        self.viendo_consulta = False
        self.años_seleccionados = [] 