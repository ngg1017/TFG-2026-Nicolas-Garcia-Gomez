from fpdf import FPDF
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color, TextoColor
from fpdf.fonts import FontFace
from fpdf.enums import TableCellFillMode
import pandas as pd

class PDF(FPDF):
    def header(self):
        #Fuente: helvetica negrita 15
        self.set_font("helvetica", style="B", size=15)
        #Calcular el ancho del titulo
        width = self.get_string_width(self.title) + 6
        self.set_x((210 - width) / 2)
        #Establecemos los colores del texto
        self.set_draw_color(Color.OSCURO.value)
        self.set_fill_color(Color.ACENTO.value)
        self.set_text_color(Color.OSCURO.value)
        #Ancho del recuadro
        self.set_line_width(1)
        #Imprimimos el titulo:
        self.cell(
            width,
            9,
            self.title,
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            fill=True,
        )
        #Salto de linea
        self.ln(10)

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
    def cuerpo_capitulo(self, titulo, descripcion, datos):
        self.set_font("Times", size=12)
        self.multi_cell(0, 5, descripcion)
        self.ln(2)
        for docu in datos:
            #Reseteamos X manualmente por seguridad 
            self.set_x(10) 
            self.multi_cell(0, 10, f"En el año {docu["name"]} tuvimos un@ {titulo} de {docu["valor"]}%", align="C")
        
    
    def añadir_grafico(self, imagen, ancho=120):
        #Calculamos la posición X para centrar (A4 = 210mm)
        pos_x = (210 - ancho) / 2

        #Guardamos la posicion Y actual para poner la imagen
        pos_y = self.get_y() + 5
        
        self.image(imagen, x=pos_x, y=pos_y, w=ancho)

    #Impresion del capitulo
    def imp_capitulo(self, num, titulo, descripcion, datos, imagen):
        self.add_page()
        self.titulo_capitulo(num, titulo)
        self.cuerpo_capitulo(titulo, descripcion, datos)
        self.añadir_grafico(imagen)
    
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