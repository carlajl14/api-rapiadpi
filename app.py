from flask import Flask, request, send_file, jsonify
from PIL import Image
from fpdf import FPDF
import os

app = Flask(__name__)

# Define tu secreto de RapidAPI (asegúrate de mantener esto seguro)
RAPIDAPI_SECRET = '5ec60b00-eddc-11ef-9c15-59f608f93374'

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    # Verificar el encabezado de RapidAPI
    rapidapi_secret = request.headers.get('X-RapidAPI-Proxy-Secret')
    if rapidapi_secret != RAPIDAPI_SECRET:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    if 'image' not in request.files:
        return "No file part", 400

    file = request.files['image']

    if file.filename == '':
        return "No selected file", 400

    try:
        # Guarda la imagen temporalmente para poder agregarla al PDF
        temp_image_path = f"/tmp/{file.filename}"
        image = Image.open(file)
        image.save(temp_image_path)
        
        # Crea el PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_path, x=10, y=10, w=100)
        
        # Guarda el PDF temporalmente
        pdf_output = f"/tmp/{file.filename}.pdf"
        pdf.output(pdf_output)
        
        # Elimina la imagen temporal
        os.remove(temp_image_path)
        
        # Envía el archivo PDF como respuesta
        return send_file(pdf_output, as_attachment=True, download_name=f"{file.filename}.pdf", mimetype='application/pdf')

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=False)
