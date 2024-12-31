from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import os
from werkzeug.utils import secure_filename
import zipfile
import io
import uuid

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resize', methods=['POST'])
def resize_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('images')
    width = int(request.form.get('width', 100))
    height = int(request.form.get('height', 100))

    # Create a zip file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{str(uuid.uuid4())}_{filename}"

                # Open and resize image
                img = Image.open(file)
                resized_img = img.resize((width, height), Image.LANCZOS)

                # Save resized image to memory
                img_byte_arr = io.BytesIO()
                resized_img.save(img_byte_arr, format=img.format)
                img_byte_arr.seek(0)

                # Add to zip file
                zf.writestr(f"resized_{filename}", img_byte_arr.getvalue())

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='resized_images.zip'
    )


if __name__ == '__main__':
    app.run(debug=True)