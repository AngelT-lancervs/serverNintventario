import json
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import sys
import os

# Obtener la ruta del archivo PDF desde los argumentos
if len(sys.argv) != 2:
    print("Uso: python report_pdf_generator.py <output_file_path>")
    sys.exit(1)

file_path = sys.argv[1]
json_url = 'https://servernintventario.onrender.com/get-json'

print(f"Solicitando JSON desde: {json_url}")

# Descargar el archivo JSON
try:
    response = requests.get(json_url)
    response.raise_for_status()
    print(f"Estado de la respuesta del JSON: {response.status_code}")

    products = response.json()

    # Filtrar los productos que cumplen con los criterios
    filtered_products = [
        product for product in products
        if (product.get('stock_inicial', 0) != product.get('stock_final', 0)) or (product.get('state', '') == 'unchecked')
    ]

    # Crear un nuevo archivo PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, alignment=1)
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Heading1'], fontSize=12, alignment=1)
    table_data_style = ParagraphStyle('TableData', parent=styles['BodyText'], fontSize=10)

    # Título
    title = Paragraph("Reporte de Productos", title_style)
    elements.append(title)
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio

    # Productos revisados
    checked_products = [
        product for product in filtered_products if product.get('state', '') == 'checked'
    ]
    # Productos no revisados
    unchecked_products = [
        product for product in filtered_products if product.get('state', '') == 'unchecked'
    ]

    def create_table(data, table_title):
        elements.append(Paragraph(table_title, title_style))
        elements.append(Paragraph(" ", styles['Normal']))  # Espacio

        # Ajuste para cada fila
        formatted_data = [
            [Paragraph(cell, table_data_style) if isinstance(cell, str) else cell for cell in row]
            for row in data
        ]

        table = Table(formatted_data, colWidths=[1 * inch, 2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica')
        ]))
        elements.append(table)

    # Datos para productos revisados
    checked_data = [
        ["Código", "Nombre", "Stock Inicial", "Stock Final", "Estado"]
    ]
    for product in checked_products:
        checked_data.append([
            product.get('codigo', 'N/A'),
            product.get('nombre', 'N/A'),
            product.get('stock_inicial', 'N/A'),
            product.get('stock_final', 'N/A'),
            product.get('state', 'N/A')
        ])
    create_table(checked_data, "Productos Revisados")

    # Datos para productos no revisados
    unchecked_data = [
        ["Código", "Nombre", "Stock Inicial", "Stock Final", "Estado"]
    ]
    for product in unchecked_products:
        unchecked_data.append([
            product.get('codigo', 'N/A'),
            product.get('nombre', 'N/A'),
            product.get('stock_inicial', 'N/A'),
            product.get('stock_final', 'N/A'),
            product.get('state', 'N/A')
        ])
    create_table(unchecked_data, "Productos No Revisados")

    # Productos con diferencia en el stock
    stock_diff_products = [
        product for product in filtered_products
        if product.get('stock_inicial', 0) != product.get('stock_final', 0)
    ]

    # Datos para productos con diferencia en el stock
    stock_diff_data = [
        ["Código", "Nombre", "Stock Inicial", "Stock Final", "Estado"]
    ]
    for product in stock_diff_products:
        stock_diff_data.append([
            product.get('codigo', 'N/A'),
            product.get('nombre', 'N/A'),
            product.get('stock_inicial', 'N/A'),
            product.get('stock_final', 'N/A'),
            product.get('state', 'N/A')
        ])
    create_table(stock_diff_data, "Productos con Diferencia de Stock")

    # Generar el archivo PDF
    doc.build(elements)
    print(f"Archivo PDF guardado en: {file_path}")
    sys.exit(1)

except requests.RequestException as e:
    print(f"Error al descargar el archivo JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error al generar el archivo PDF: {e}")
    sys.exit(1)
