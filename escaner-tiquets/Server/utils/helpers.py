from pdf2image import convert_from_bytes
import base64
import os
from io import BytesIO
from gtts import gTTS
from ultralytics import YOLO
import json
from datetime import datetime
import requests

from azure.storage.blob import BlobServiceClient, ContainerClient


from .fake_outputs import fake_products, fake_image, fake_audio
from .model.relate_bbox import relate_bbox

def pdf_to_image(str_pdf):

    bytes_object = base64.b64decode(str_pdf)
    
    # apt-get install poppler-utils
    # Convertim el pdf a imatge
    images = convert_from_bytes(bytes_object)
    image_pil = images[0]
    
    # Guardem la imatge a objecte bytes en format JPGE. Això ho fem en memoria sense guardar-ho enlloc.
    # Basicament li assignem un format a la imatge.
    image_bytes = BytesIO()
    image_pil.save(image_bytes, format='PNG')

    # Agafem la cadena de bytes i ho guardem a la variable.
    image_content = image_bytes.getvalue()
    
    # Codifiquem la imatge a base64
    image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

    return image_base64, image_content

def img_base64_to_bytes(str_img):
    bytes_object = base64.b64decode(str_img)

    return str_img, bytes_object

def make_inference_with(image):
    yolo_model = './utils/model/best.pt'
    model = YOLO(yolo_model)

    inference = model(image)
    resultat = relate_bbox(inference, image)

    return resultat


def extract_products_from_ticket(json_tiquet):
    products = json_tiquet['products']
    total = json_tiquet['total_amb_IVA']

    text = "Els productes del tiquet són: \n"

    for product in products:
        unitats = product['quantitat']
        descripcio = product['descripcio']
        preu_producte =product['import']
        
        text += f"{unitats} unitats de {descripcio} amb un preu de {preu_producte} euros. \n"

    text += f"El preu final de tots els productes és: {total} euros."

    return text

def text_to_speech(text, lang = 'ca'):
    # return fake_audio

    output = gTTS(text=text, lang=lang, slow=False)

    output.save("output.mp3")

    # Llegim el fitxer i el convertim a base64, després el borrem del servidor.
    with open("output.mp3", "rb") as audio_file:
        base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')
    
    os.remove("output.mp3")

    return base64_audio



# Dades d'accés azure
connection_string = 'DefaultEndpointsProtocol=https;AccountName=projecteiabd;AccountKey=SIJUq70OANvk90EHQNBR6ZSmIg5ITOHIwABgzZ3NvU64t2IVEYeB/sXu9ioLpPo9FeAgm4z7+Rze+ASt1eRbzQ==;EndpointSuffix=core.windows.net'


def save_json_bronze(json_string, user_id):
    # pip install azure-mgmt-storage
    # pip install azure-storage-blob

    # Container d'azure on ho penjarem.
    container_name = 'bronze'

    # Convertim el document a JSON si és necessari - ES POT BORRAR?
    if isinstance(json_string, dict):
        json_string = json.dumps(json_string)

    # Agafem la data d'avui i la guardem en el format que ens interessa
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%d%m%Y_%H%M%S")
    current_datetime_formated = current_datetime.strftime("%d%m%Y")

    # Creem el path on hem de guardar el json
    # /id usuari/data formatejada/timestamp
    path = f"{user_id}/{current_datetime_formated}/{timestamp}.json"

    # Connectem al servei de blob d'Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)

    # Pujem el fitxer JSON al blob d'Azure
    blob_client.upload_blob(json_string, overwrite=True)

    print('Pujat a Azure Data Lake - Bronze')

def save_img_raw(image_path, user_id):

    # Container d'azure on ho penjarem.
    container_name = 'raw'

    # Agafem la data d'avui i la guardem en el format que ens interessa
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%d%m%Y_%H%M%S")
    current_datetime_formated = current_datetime.strftime("%d%m%Y")

    # Creem el path on hem de guardar el json
    # /id usuari/data formatejada/timestamp
    path = f"{user_id}/{current_datetime_formated}/{timestamp}.png"

    # Connectem al servei de blob d'Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)

    # Pujem el fitxer JSON al blob d'Azure
    blob_client.upload_blob(image_path, overwrite=True)

    print('Pujat a Azure Data Lake - Raw')



__all__ = ['img_base64_to_bytes', 'pdf_to_image', 'make_inference_with', 'text_to_speech', 'extract_products_from_ticket', 'save_json_bronze', 'save_img_raw']