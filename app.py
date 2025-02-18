from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
import os
import base64  # Asegurarse de importar el módulo base64

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    try:
        # Imprimir el contenido recibido para depuración
        print("Contenido de request.files:")
        print(request.files)
        
        if 'image' in request.files:
            file = request.files['image']
            # Verifica si se ha seleccionado un archivo
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400

            # Guarda el archivo temporalmente
            temp_image_path = f"/tmp/{file.filename}"
            file.save(temp_image_path)
            print(f"Archivo {file.filename} guardado temporalmente en {temp_image_path}")

            # Abre la imagen desde el archivo temporal
            try:
                image = Image.open(temp_image_path)
                image.verify()  # Verifica que la imagen sea válida
                image = Image.open(temp_image_path)  # Reabrir la imagen
            except UnidentifiedImageError:
                return jsonify({"error": "Cannot identify image file"}), 400

        else:
            return jsonify({"error": "No file part"}), 400

        # Crear el PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_path, x=10, y=10, w=100)
        
        # Guarda el PDF temporalmente
        pdf_output = f"/tmp/{os.path.splitext(file.filename)[0]}.pdf"
        pdf.output(pdf_output)
        print("PDF guardado temporalmente en:", pdf_output)
        
        # Elimina la imagen temporal
        os.remove(temp_image_path)

        # Lee el archivo PDF y codifícalo en base64
        with open(pdf_output, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Elimina el archivo PDF temporal
        os.remove(pdf_output)

        # Devuelve el archivo PDF codificado en base64
        return jsonify({"file": pdf_base64, "filename": f"{os.path.basename(pdf_output)}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
