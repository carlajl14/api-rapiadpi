from flask import Flask, request, jsonify
from PIL import Image
from fpdf import FPDF
import os
import base64

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

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
        
        # Lee el archivo PDF y codifícalo en base64
        with open(pdf_output, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        # Elimina el archivo PDF temporal
        os.remove(pdf_output)
        
        # Devuelve el archivo PDF codificado en base64
        return jsonify({"file": pdf_base64, "filename": f"{file.filename}.pdf"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
