from fpdf import FPDF
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from fpdf.fonts import FontFace
from fpdf.enums import TableCellFillMode
import pandas as pd

class PDF(FPDF):
    #Aplica el pie de pagina
    def footer(self):
        #Indice de pagina
        self.set_y(-15)
        self.set_font("helvetica", style="I", size=8)
        self.set_text_color(128)
        #Numero de pagina
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    #Titulo del capitulo
    def titulo_capitulo(self, num, titulo):
        self.set_font("helvetica", size=12)
        self.set_fill_color(Color.ACENTO.value)
        #Imprimimos el nombre del capitulo:
        self.cell(
            0,
            6,
            f"Indicador {num}: {titulo}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
            fill=True,
        )
        self.ln(4)

    #Texto del capitulo
    def cuerpo_capitulo(self, descripcion, datos):
        self.set_font("Times", size=12)
        self.multi_cell(0, 5, descripcion)
        self.ln(2)
        for docu in datos:
            #Reseteamos X manualmente por seguridad 
            self.set_x(10) 
            self.multi_cell(0, 10, f"En el año {docu["name"]} tuvimos un {docu["valor"]}%", align="L")
    
    #Añadimos el grafico calculado con matplotlib
    def añadir_grafico(self, imagen, ancho=140):
        #Calculamos la posición X para centrar (A4 = 210mm)
        pos_x = (210 - ancho) / 2
        #Guardamos la posicion Y actual para poner la imagen
        pos_y = self.get_y() + 25
        self.image(imagen, x=pos_x, y=pos_y, w=ancho)
    
    #Texto que introducimos en funcion de la tendencia y del r2
    def analisis_final(self, tendencia, r2):
        self.set_font("Times", size=12)
        self.ln(2)
        #Analisis de la tendencia
        if tendencia > 0.5:
            texto_tendencia = f"El indicador tiene una tendencia ascendente, creciendo una media de {tendencia:.4f} unidades por año"
        elif tendencia < -0.1:
            texto_tendencia = f"El indicador muestra una tendencia favorable a la baja, reduciéndose un {tendencia:.4f} anual"
        else:
            texto_tendencia = f"El indicador se mantiene estable a lo largo del periodo analizado con una variacion anual de {tendencia:.4f}"
        
        self.multi_cell(0, 5, texto_tendencia)
        self.ln(2)

        #Analisis del r2
        if r2 > 0.7:
            texto_r2 = f"Una R² de {r2:.4f} indica que el indicador sigue una tendencia muy clara. Los cambios año tras año son constantes "\
            "y el modelo es muy robusto para hacer predicciones."
        elif 0.4 < r2 < 0.7:
            texto_r2 = f"Una R² de {r2:.4f} indica que hay una tendencia, pero los datos tienen cierta variabilidad o 'ruido' (un año hubo un pico inesperado, por ejemplo)."   
        elif 0 < r2 < 0.4:
            texto_r2 = f"Una R² de {r2:.4f} indica que el indicador fluctúa mucho. No se puede decir que haya una tendencia lineal clara; los cambios "\
            "anuales son probablemente debidos a factores aleatorios o puntuales."
        elif r2 == 0:
            texto_r2 = "Cuando la desviación estándar clínica es insignificante (menos del 1%), el modelo de regresión lineal pierde validez explicativa. " \
            "En estos casos, el protocolo estadístico indica considerar el indicador como 'Estable' en lugar de forzar una tendencia matemática que carece de significancia clínica." 
        else:
            texto_r2 = f"Una R² negativa de {r2:.4f} significa que el indicador no presenta un comportamiento lineal predecible"            

        self.multi_cell(0, 5, texto_r2)
    
    #Añadimos una primera pagina explicando que contiene el documento
    def primara_pagina(self):
        self.add_page()
        #Titulo principal
        self.set_font("Times", style="B", size=15)
        self.multi_cell(0, 10, "Guía de Interpretación de Gráficos Clínicos", align="C")
        self.ln(10)

        #Introduccion
        self.set_font("Times", size=12)
        self.multi_cell(0, 7, (
            "Este informe presenta la evolución de los indicadores de calidad de la Unidad de "
            "Cuidados Intensivos mediante representaciones visuales avanzadas. Para una correcta "
            "lectura de los resultados, se deben tener en cuenta los siguientes elementos gráficos:"
        ))
        self.ln(8)

        #Seccion 1: Tendencia y R2
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "1. Análisis de Tendencia y Fiabilidad (R2)", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "- Línea Rosa Continua: Representa la tendencia lineal. Una inclinación descendente "
            "indica una mejora en indicadores de resultados negativos (mortalidad, infecciones).\n"
            "- Valor R2 (Coeficiente de Determinación): Indica la fiabilidad del modelo (0 a 1). "
            "Valores cercanos a 1 sugieren una tendencia constante y predecible; valores cercanos "
            "a 0 indican fluctuaciones erráticas."
        ))
        self.ln(5)
        
        #Seccion 2: Estabilidad y Media
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "2. Estabilidad y Media Histórica", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "- Línea Verde Punteada: Representa la Media Histórica del periodo analizado. Sirve "
            "como referencia para identificar si el año actual se sitúa por encima o por debajo "
            "de lo habitual en la unidad.\n"
            "- Franja Sombreada: Marca el área de variabilidad normal. Los valores fuera de esta "
            "franja se consideran anomalías estadísticas o eventos reseñables."
        ))
        self.ln(5)
        
        #Seccion 3: Barras de Error
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "3. Barras de Error (Variabilidad Interna)", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "Las 'antenas' sobre las columnas representan la Desviación Estándar:\n"
            "- Barras Cortas: Indican datos homogéneos (pacientes con comportamiento similar).\n"
            "- Barras Largas: Indican datos heterogéneos (alta variabilidad entre pacientes, lo "
            "que sugiere que el promedio anual está influenciado por casos extremos)."
        ))
        self.ln(5)

        #Seccion 4: Identificacion de Eventos Centinela (Regla 2-Sigma)
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "4. Identificación de Eventos Centinela (Regla 2-Sigma)", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "Para evitar alarmas injustificadas por fluctuaciones menores, se aplica la regla de las dos "
            "desviaciones estándar (2-Sigma). Solo se marcan como eventos significativos aquellos años que "
            "superan este umbral crítico (donde solo se sitúa el 5% de los casos más extremos):\n"
            "- Barra Roja: Alerta por empeoramiento significativo que requiere revisión de protocolos.\n"
            "- Barra Verde: Éxito clínico excepcional que debe ser analizado como 'buena práctica'.\n"
            "- Barra Azul: Comportamiento dentro de la variabilidad habitual del servicio."
        ))

    #Impresion del capitulo
    def imp_capitulo(self, num, titulo, descripcion, datos, imagen, tendencia, r2):
        self.add_page()
        self.titulo_capitulo(num, titulo)
        self.cuerpo_capitulo(descripcion, datos)
        self.añadir_grafico(imagen)
        self.analisis_final(tendencia, r2)
    
    #Metodo para incluir tablas
    def incluir_tabla(self, csv: pd.DataFrame):
        self.add_page()
        #Color de las lineas
        self.set_draw_color(TextoColor.PRIMARIO.value)
        self.set_line_width(0.3)
        headings_style = FontFace(emphasis="BOLD", color=TextoColor.PRIMARIO.value, fill_color=Color.OSCURO.value, size_pt=10)
        with self.table(
            cell_fill_color=Color.ACENTO.value,
            cell_fill_mode=TableCellFillMode.ROWS,
            headings_style=headings_style,
            line_height=6,
        ) as table:
            #La primera fila de los titulos
            table.row(csv.columns.tolist())
            for fila in csv.values.tolist():
                row = table.row()
                for i, celda in enumerate(fila):
                    texto_celda = str(celda) if celda is not None else ""
                    
                    #Si es la primera columna alineamos a la izquierda y le damos otro color
                    if i == 0:
                        #Si tiene muchas columnas reduce el tamaño de la letra
                        if len(csv.columns.tolist()) > 8:
                            tamaño = 7
                        else:
                            tamaño=12
                        aliacion="L"
                        estilo = FontFace(color=TextoColor.PRIMARIO.value, fill_color=Color.OSCURO.value, size_pt=tamaño)
                    else:
                        aliacion="C"
                        estilo = FontFace(color=TextoColor.SECUNDARIO.value)
                    row.cell(texto_celda, align=aliacion, style=estilo)