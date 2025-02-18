from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
import os
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    try:
        # Imprimir el contenido recibido para depuración
        print("Contenido de request.json:")
        print(request.json)
        
        # Verifica si se recibieron datos en formato JSON
        if 'image' not in request.json or 'data' not in request.json['image']:
            return jsonify({"error": "No file part"}), 400

        image_data = request.json['image']['data']
        
        # Decodificar la imagen en base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        
        # Usar BytesIO para tratar los bytes como un archivo
        image = Image.open(BytesIO(image_bytes))
        
        # Verificar que la imagen sea válida
        try:
            image.verify()
        except UnidentifiedImageError:
            return jsonify({"error": "Cannot identify image file"}), 400

        # Guardar temporalmente la imagen
        temp_image_path = "/tmp/temp_image.jpg"
        image.save(temp_image_path)

        # Crear el PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_path, x=10, y=10, w=100)
        
        # Guardar el PDF temporalmente
        pdf_output = "/tmp/temp_image.pdf"
        pdf.output(pdf_output)
        
        # Leer el archivo PDF y codificarlo en base64
        with open(pdf_output, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Eliminar archivos temporales
        os.remove(temp_image_path)
        os.remove(pdf_output)

        # Devolver el archivo PDF codificado en base64
        return jsonify({"file": pdf_base64, "filename": "converted.pdf"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
