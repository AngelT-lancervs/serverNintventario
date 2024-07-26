"""
Script para cargar datos del inventario desde un archivo Excel y guardarlos en formato JSON.
"""
import json
import pandas as pd

EXCEL_FILE = 'nintventario\\src\\files\\inventario.xlsx'
df = pd.read_excel(EXCEL_FILE, skiprows=5)

print("Columnas en el DataFrame:", df.columns)

df.columns = df.columns.str.strip()

print("Primeras 20 filas del DataFrame:")
print(df.head(20))

filtered_df = df[['Código', 'Nombre', 'Stock Final']]
filtered_df.columns = ['codigo', 'nombre', 'stock']
data = filtered_df.to_dict(orient='records')

JSON_FILE_PATH = 'nintventario\\src\\files\\inventario.json'

with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"Datos guardados en {JSON_FILE_PATH}")

print("Código\tNombre\tStock")
for item in data:
    print(f"{item['codigo']}\t{item['nombre']}\t{item['stock']}")
