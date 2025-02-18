from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
import os
import base64

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    try:
        # Verifica si se recibieron archivos en la solicitud
        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['image']
        
        # Verifica si se ha seleccionado un archivo
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Guarda el archivo temporalmente
        temp_image_path = f"/tmp/{file.filename}"
        file.save(temp_image_path)

        try:
            # Abre la imagen desde el archivo temporal
            image = Image.open(temp_image_path)
            image.verify()  # Verifica que la imagen sea válida
        except UnidentifiedImageError:
            return jsonify({"error": "Cannot identify image file"}), 400

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
