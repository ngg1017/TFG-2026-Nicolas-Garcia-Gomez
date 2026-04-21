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
        self.ln(2)

    #Texto del capitulo
    def cuerpo_capitulo(self, descripcion, datos, titulo, ind_especialidades=False):
        self.set_font("Times", size=11)
        self.multi_cell(0, 5, descripcion)
        self.ln(5)
        
        #Convertimos los datos a lista por si vienen como objeto "zip"
        datos_lista = list(datos) 
        
        #Altura de la fila
        altura_fila = 10
        
        if ind_especialidades == True:
            #Para especialidades (textos largos): 2 columnas de 95mm de ancho
            ancho_col = 95 
            #Extraemos la especialidad
            especialidad = titulo.split(":")[1].strip()
            
            for i, (año, valor) in enumerate(datos_lista):
                #Texto a añadir
                texto = f"Año {año} en {especialidad}: {valor}% de ingresos"
                #Creamos la celda con su texto, ancho y altura
                self.cell(ancho_col, altura_fila, texto, align="C")
                
                #Si estamos en la segunda columna (indice impar), hacemos salto de linea
                if (i + 1) % 2 == 0:
                    self.ln(altura_fila)
            
            #Si el numero total de datos es impar, forzamos el salto de linea final
            if len(datos_lista) % 2 != 0:
                self.ln(altura_fila)

        else:
            #Para datos generales (textos cortos): 3 columnas de 63mm de ancho
            ancho_col = 63 
            
            for i, docu in enumerate(datos_lista):
                #Texto a añadir
                texto = f"Año {docu["name"]}: {docu["valor"]}%"
                #Creamos la celda con su texto, ancho y altura
                self.cell(ancho_col, altura_fila, texto, align="C")
                
                #Si estamos en la tercera columna, hacemos salto de linea
                if (i + 1) % 3 == 0:
                    self.ln(altura_fila)
                    
            #Si no completamos la ultima fila de 3, forzamos el salto
            if len(datos_lista) % 3 != 0:
                self.ln(altura_fila)
    
    #Añadimos el grafico calculado con matplotlib
    def añadir_grafico(self, imagen, ancho=140):
        #Calculamos la posición X para centrar (A4 = 210mm)
        pos_x = (210 - ancho) / 2

        #Al no pasar Y, FPDF coloca la imagen en la Y actual 
        self.image(imagen, x=pos_x, w=ancho)
        
        #Reseteamos la X al margen izquierdo (10mm)
        self.set_x(10)
    
    @staticmethod
    #Funcion que evalua la pendiente y la r2 para usarlo tanto en el informe como en reflex
    def texto_tendencia_r2(pendiente_tend, r2):
        texto_tendencia =""
        texto_r2 =""
        texto_error =""

        #Analisis de la tendencia(Rango de estabilidad ajustado a -0.1 y 0.1)
        if pendiente_tend > 0.1:
            texto_tendencia = f"El indicador muestra una tendencia ascendente, con una variación media de +{pendiente_tend:.4f} puntos anuales."
        elif pendiente_tend < -0.1:
            #Usamos abs() para quitar el signo negativo al leer la frase
            texto_tendencia = f"El indicador presenta una tendencia descendente, reduciéndose a un ritmo de {abs(pendiente_tend):.4f} puntos por año."
        else:
            texto_tendencia = f"El indicador se mantiene estable a lo largo del periodo, con una variación interanual mínima ({pendiente_tend:.4f})."
        
        #Analisis del r2
        if r2 == 0:
            texto_r2 = ("Dado que la amplitud histórica es mínima, el modelo asume una estabilidad estructural. "
                        "El protocolo estadístico descarta forzar una tendencia matemática que carece de significancia clínica, "
                        "definiendo el indicador globalmente como 'Estable'.")
        elif r2 >= 0.7:
            texto_r2 = f"Con un coeficiente de determinación (R²) de {r2:.4f}, la tendencia es sólida y consistente. "\
                       "Los cambios anuales siguen un patrón claro, lo que otorga gran fiabilidad descriptiva al modelo histórico."
        elif r2 >= 0.4:
            texto_r2 = f"Con un R² de {r2:.4f}, existe una tendencia visible, pero la serie presenta moderada variabilidad. "\
                       "Factores puntuales de ciertos años generan 'ruido' estadístico alrededor de la línea principal."
        elif r2 > 0:
            texto_r2 = f"El R² de {r2:.4f} revela una alta dispersión. Los datos fluctúan significativamente, por lo que "\
                       "no se puede confirmar un patrón de evolución lineal claro; la variabilidad obedece principalmente a factores estacionales o aleatorios."
        else:
            texto_r2 = f"El indicador (R²: {r2:.4f}) no presenta un comportamiento lineal descriptible por este modelo matemático."
        
        #Analisis de la variabilidad y el Error Tipico
        texto_error = ("Nota metodológica: Las líneas paralelas que envuelven la tendencia "
                       "establecen un 'pasillo de normalidad' histórico. Si el valor real de un año excede estas marcas, "
                       "señala una alteración estadísticamente significativa frente a la evolución general del servicio.")
        
        return texto_tendencia, texto_r2, texto_error
    
    #Texto que introducimos en funcion de la tendencia y del r2
    def analisis_final(self, texto_tendencia, texto_r2, texto_error):
        self.set_font("Times", size=11)
        self.ln(5)
        
        self.set_x(10)
        self.multi_cell(0, 5, texto_tendencia)
        self.ln(2)
        
        self.set_x(10)
        self.multi_cell(0, 5, texto_r2)
        self.ln(2)
        
        self.set_font("Times", style="I", size=11)        
        self.set_x(10)
        self.multi_cell(0, 5, texto_error)
        self.set_font("Times", size=11)
    
    #Añadimos una primera pagina explicando que contiene el documento
    def primera_pagina(self):
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
            "- Línea Horizontal Verde Punteada: Representa la Media Histórica del periodo analizado. Sirve "
            "como referencia para identificar si el año actual se sitúa por encima o por debajo "
            "de lo habitual en la unidad."
        ))
        self.ln(5)
        
        # Seccion 3: Pasillo de Confianza
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "3. Pasillo de Confianza (Error Típico Interanual)", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "La franja rosa sombreada que envuelve a la línea de tendencia representa el Error Típico Interanual del modelo. "
            "Esta banda visual conforma un 'pasillo de normalidad' que evalúa la estabilidad histórica del indicador:\n"
            "- Franja Estrecha: Indica una evolución muy estable y predecible. Las variaciones entre los distintos años "
            "son mínimas y se mantienen muy cercanas a la tendencia central.\n"
            "- Franja Ancha: Refleja una mayor variabilidad o 'ruido' estadístico a lo largo del periodo analizado.\n"
            "Si la columna de un año específico sobresale de los límites de este pasillo, señala una desviación "
            "estadísticamente significativa respecto a la evolución general esperada para el servicio."
        ))
        self.ln(5)

        #Seccion 4: Identificacion de Eventos Centinela (Regla 2-Sigma)
        self.set_font("Times", style="B", size=13)
        self.cell(0, 8, "4. Identificación de Eventos Centinela (Regla 2-Sigma)", ln=True)
        self.set_font("Times", size=12)
        self.multi_cell(0, 6, (
            "Para evitar falsas alarmas provocadas por fluctuaciones estadísticas normales, el sistema evalúa "
            "cada período usando la regla de las dos Desviaciones Estándar (2-Sigma). Las columnas o puntos del gráfico (incluyendo una línea vertical) cambiarán "
            "de color solo si superan este umbral crítico. La dirección del color Verde y Rojo dependerá del indicador, pero siempre reflejarán lo mismo:\n"
            "- Color Rojo: Alerta por empeoramiento del resultado. Señala una desviación significativa que "
            "requiere la revisión de los procesos.\n"
            "- Color Verde: Alerta por mejora del resultado. Señala una desviación significativa que "
            "requiere la revisión de los procesos.\n"
            "- Color Azul: Comportamiento estable y dentro de la normalidad esperada "
            "del servicio."
        ))
        self.ln(5)

    #Impresion del capitulo
    def imp_capitulo(self, num, titulo, descripcion, datos, imagen, pendiente_tend, r2, ind_especialidades = False):
        self.add_page()
        self.titulo_capitulo(num, titulo)
        self.cuerpo_capitulo(descripcion, datos, titulo, ind_especialidades) 
        self.añadir_grafico(imagen)
        texto_tendencia, texto_r2, texto_error = self.texto_tendencia_r2(pendiente_tend, r2)
        self.analisis_final(texto_tendencia, texto_r2, texto_error)
    
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