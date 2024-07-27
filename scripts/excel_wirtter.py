import sys
from openpyxl import Workbook
import requests

if len(sys.argv) != 2:
    print("Uso: python python_script.py <output_file_path>")
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

    # Crear un nuevo archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    # Escribir los encabezados en la hoja de cálculo
    headers = ["Código", "Nombre", "Stock Inicial", "Stock Final"]
    ws.append(headers)

    # Escribir los datos de los productos en la hoja de cálculo
    for product in products:
        ws.append([
            product.get('codigo', 'N/A'),
            product.get('nombre', 'N/A'),
            product.get('stock_inicial', 'N/A'),
            product.get('stock_final', 'N/A')
        ])

    # Guardar el archivo Excel
    wb.save(file_path)
    print(f"Archivo Excel guardado en: {file_path}")
    sys.exit(1)

except requests.RequestException as e:
    print(f"Error al descargar el archivo JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error al generar el archivo Excel: {e}")
    sys.exit(1)
