import datetime
import json
import logging
import os
import subprocess


UPLOAD_DIR = 'uploads'
PYTHON_SCRIPT_PATH = '/scripts/excel_wirtter.py'
PYTHON_SCRIPT_PATH_PDF = 'scripts/report_pdf_generator.py' 
UPLOAD_URL = 'https://servernintventario.onrender.com/upload-excel/'
UPLOAD_URL_PDF='https://servernintventario.onrender.com/upload-pdf/'

output_file_path = os.path.join(UPLOAD_DIR, 'generated_pdf.pdf')
        # Ejecutar el script de Python para generar el PDF
result = subprocess.run(
            ['python', PYTHON_SCRIPT_PATH_PDF, output_file_path],
            capture_output=True, text=True
        )

print(output_file_path)
print(result)