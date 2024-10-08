import datetime
import json
import logging
import os
import subprocess
import uuid
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from numpy import generic
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import ProductSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


UPLOAD_DIR = 'uploads'
PYTHON_SCRIPT_PATH = 'scripts/excel_wirtter.py'
PYTHON_SCRIPT_PATH_PDF = 'scripts/report_pdf_generator.py' 
UPLOAD_URL = 'https://servernintventario.onrender.com/upload-excel/'
UPLOAD_URL_PDF='https://servernintventario.onrender.com/upload-pdf/'

@api_view(['POST'])
def login(request):

    user=get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):

        return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created =Token.objects.get_or_create(user=user)
    serializer=UserSerializer(instance=user)
    return Response({"Token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_user(request):
    """
    Vista que maneja la solicitud GET para listar todos los usuarios.
    """
    # Obtiene todos los usuarios
    queryset = User.objects.all()

    # Serializa el queryset
    serializer = UserSerializer(queryset, many=True)

    # Retorna la respuesta serializada
    return Response(serializer.data)


@api_view(['POST'])
def register(request):

    serializer =  UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        user=User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['passwor'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    print(request.user.password)
    return Response("You are logged with {}".format(request.user.username), status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_json(request):
    try:
        # Verifica si hay datos JSON en la solicitud
        if 'json_data' not in request.data:
            return HttpResponseBadRequest(json.dumps({"error": "No JSON data provided"}), content_type='application/json')

        # Obtiene la lista de productos desde json_data
        products_list = request.data['json_data']

        # Verifica si json_data es una lista
        if not isinstance(products_list, list):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON format. Expected a list of products."}), content_type='application/json')

        # Crea el directorio de subida si no existe
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        file_path = os.path.join(UPLOAD_DIR, 'data.json')
        
        # Guarda el contenido JSON en un archivo
        with open(file_path, 'w') as f:
            json.dump(products_list, f)

        return JsonResponse({"message": "JSON data processed and saved successfully!"}, status=status.HTTP_200_OK)

    except Exception as e:
        return HttpResponseServerError(json.dumps({"error": str(e)}), content_type='application/json')

@api_view(['GET', 'DELETE'])
def get_json(request):
    file_path = os.path.join(UPLOAD_DIR, 'data.json')
    if request.method == 'GET':
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/json')
        else:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        try:
            # Verifica si el archivo existe y lo elimina
            if os.path.exists(file_path):
                os.remove(file_path)
                return Response({"message": "File deleted successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponseServerError(json.dumps({"error": str(e)}), content_type='application/json')
        

# Configurar logging para depuración
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_excel(request):
    request_id = str(uuid.uuid4())  # Generar un ID único para esta solicitud
    logger.debug(f"Procesando solicitud {request_id}")
    try:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        output_file_path = os.path.join(UPLOAD_DIR, 'generated_file.xlsx')
        logger.debug(f"Ejecutando script de Python para solicitud {request_id}...")

        result = subprocess.run(
            ['python', PYTHON_SCRIPT_PATH, output_file_path],
            capture_output=True, text=True
        )
        logger.debug(f"Resultado del script para solicitud {request_id}: {result.stdout}")
        logger.error(f"Errores del script para solicitud {request_id}: {result.stderr}")

        if result.returncode != 0:
            logger.error(f"Error en el script para solicitud {request_id}: {result.stderr}")
            return JsonResponse({"error": f"Script error: {result.stderr}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.debug(f"Ruta del archivo generado para solicitud {request_id}: {output_file_path}")

        with open(output_file_path, 'rb') as f:
            file_data = f.read()

        upload_response = requests.post(UPLOAD_URL, files={'file': file_data})
        upload_response.raise_for_status()  
        if upload_response.status_code == 200:
            logger.debug(f"Archivo subido exitosamente para solicitud {request_id}!")
            response = HttpResponse(file_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="generated_file.xlsx"'
            return response
        else:
            logger.error(f"Fallo al subir el archivo para solicitud {request_id}. Código de estado: {upload_response.status_code}")
            return JsonResponse({"error": f"Upload failed with status {upload_response.status_code}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.exception(f"Error en el endpoint upload_excel para solicitud {request_id}")
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def download_excel(request):
    file_path = os.path.join(UPLOAD_DIR, 'generated_file.xlsx')
    
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='uploaded_file.xlsx')
    else:
        return HttpResponseNotFound("File not found")
    

# Configurar el logger para depuración
logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_pdf(request):
    request_id = str(uuid.uuid4())  # Generar un ID único para esta solicitud
    logger.debug(f"Request ID: {request_id} - Inicio del método upload_pdf.")

    try:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
            logger.debug(f"Request ID: {request_id} - Directorio {UPLOAD_DIR} creado.")
        
        output_file_path = os.path.join(UPLOAD_DIR, 'generated_pdf.pdf')
        logger.debug(f"Request ID: {request_id} - Ruta de salida del PDF: {output_file_path}")

        # Ejecutar el script de Python para generar el PDF
        logger.debug(f"Request ID: {request_id} - Ejecutando el script para generar el PDF.")
        result = subprocess.run(
            ['python', PYTHON_SCRIPT_PATH_PDF, output_file_path],
            capture_output=True, text=True
        )

        # Verificar si el script se ejecutó correctamente
        if result.returncode != 0:
            logger.error(f"Request ID: {request_id} - Error en el script: {result.stderr}")
            return JsonResponse({
                "error": "Error al ejecutar el script para generar el PDF",
                "details": result.stderr
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.debug(f"Request ID: {request_id} - Script ejecutado correctamente.")

        # Verificar si el archivo PDF fue generado
        if os.path.exists(output_file_path):
            logger.debug(f"Request ID: {request_id} - Archivo PDF generado en {output_file_path}.")
            with open(output_file_path, 'rb') as f:
                file_data = f.read()

            # Subir el archivo al servidor
            logger.debug(f"Request ID: {request_id} - Subiendo el archivo PDF al servidor.")
            upload_response = requests.post(UPLOAD_URL_PDF, files={'file': file_data})
            upload_response.raise_for_status()  

            if upload_response.status_code == 200:
                logger.debug(f"Request ID: {request_id} - Archivo PDF subido correctamente.")
                response = HttpResponse(file_data, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
                return response
            else:
                logger.error(f"Request ID: {request_id} - Error al subir el archivo PDF: {upload_response.text}")
                return JsonResponse({
                    "error": "Error al subir el archivo PDF",
                    "upload_status_code": upload_response.status_code,
                    "upload_response": upload_response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Request ID: {request_id} - Archivo PDF no encontrado en {output_file_path}.")
            return JsonResponse({
                "error": "Archivo PDF no encontrado",
                "expected_path": output_file_path
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.exception(f"Request ID: {request_id} - Ocurrió un error inesperado: {str(e)}")
        return JsonResponse({
            "error": "Ocurrió un error inesperado",
            "exception": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def download_pdf(request):
    file_path = os.path.join(UPLOAD_DIR, 'generated_pdf.pdf')
    
    # Verifica si el directorio de carga existe
    if not os.path.exists(UPLOAD_DIR):
        return HttpResponseNotFound("Upload directory not found")
    
    # Verifica si el archivo existe
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf', filename='generated_pdf.pdf')
    else:
        return HttpResponseNotFound("File not found")