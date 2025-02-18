from flask import Flask, request, jsonify
from PIL import Image
from fpdf import FPDF
import os
import base64
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    try:
        # Verifica si se recibieron datos binarios
        if not request.data:
            return jsonify({"error": "No binary data received"}), 400

        # Guarda los datos binarios en un archivo temporal
        temp_binary_path = "/tmp/temp_binary_image"
        with open(temp_binary_path, 'wb') as f:
            f.write(request.data)
        
        # Abre la imagen desde el archivo temporal
        image = Image.open(temp_binary_path)
        image.verify()  # Verifica que la imagen sea válida
        
        # Guarda la imagen temporalmente para poder agregarla al PDF
        temp_image_path = "/tmp/temp_image.jpg"
        image = Image.open(temp_binary_path)
        image.save(temp_image_path)
        
        # Crea el PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_path, x=10, y=10, w=100)
        
        # Guarda el PDF temporalmente
        pdf_output = "/tmp/temp_output.pdf"
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
        return jsonify({"file": pdf_base64, "filename": "output.pdf"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
