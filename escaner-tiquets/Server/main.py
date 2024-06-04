from flask import request, jsonify, Flask
from flask_cors import CORS
import os

from utils.helpers import *

origins = ["http://127.0.0.1:5500"]

app = Flask(__name__)
CORS(app)

@app.route("/pdf/<user_id>", methods=["POST"])
def main(user_id):
 
    # agafar el body de la request (pdf)    
    if request.json:
        pdf_base64_str = request.json.get('pdfData')
        extension = request.json.get('extension')

    if extension == 'pdf':
        # Procesar el pdf:
        # 1. Convertir pdf a png
        image_base64_str, image_content = pdf_to_image(pdf_base64_str)
    else:
        image_base64_str, image_content = img_base64_to_bytes(pdf_base64_str)

    # Guarda la cadena de bytes passada a imatge
    with open("img_content.png", "wb") as img_file:
        img_file.write(image_content)

    # 2. Extreure la informació de la imatge
    ticket_info = make_inference_with('./img_content.png')
    os.remove('./img_content.png')

    products = extract_products_from_ticket(ticket_info)

    products_audio = text_to_speech(products)

    # 3. Fem la ETL
    # Penjem la foto a la capa Raw, li passem en format de bytes.
    save_img_raw(image_content, user_id)
    # Penjem el contigut en format json a la capa bronze.
    save_json_bronze(ticket_info, user_id)

    # return imatge en base64 per renderitzar-la al front i la informació del tiquet que ha extret la nn.
    response = {
        "image": image_base64_str,
        "ticket": ticket_info,
        "audio": products_audio
    }
    
    return jsonify(response), 200, {'Access-Control-Allow-Origin': '*'}

if __name__ == "__main__":
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
