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
        print("Contenido de request.form:")
        print(request.form)
        print("Contenido de request.files:")
        print(request.files)
        
        if 'image' in request.files:
            file = request.files['image']
            # Guarda el archivo temporalmente
            temp_image_path = f"/tmp/{file.filename}"
            file.save(temp_image_path)

        elif 'image' in request.form:
            image_data = request.form['image']
            
            # Quitar el prefijo 'data:image/jpeg;base64,' si está presente
            if ',' in image_data:
                image_data = image_data.split(',')[1]

            # Decodificar la imagen en base64
            image_bytes = base64.b64decode(image_data)
            # Usar BytesIO para tratar los bytes como un archivo
            image = Image.open(BytesIO(image_bytes))
            # Guardar temporalmente la imagen
            temp_image_path = "/tmp/temp_image.jpg"
            image.save(temp_image_path)

        else:
            return jsonify({"error": "No file part"}), 400

        # Crear el PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_path, x=10, y=10, w=100)
        
        # Guarda el PDF temporalmente
        pdf_output = f"/tmp/{os.path.splitext(temp_image_path)[0]}.pdf"
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
        return jsonify({"file": pdf_base64, "filename": "converted.pdf"}), 200

    except UnidentifiedImageError:
        return jsonify({"error": "Cannot identify image file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
