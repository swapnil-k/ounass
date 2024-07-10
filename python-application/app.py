from flask import Flask, request, render_template, Blueprint, jsonify
import os
import pandas as pd
import boto3
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
s3_client = boto3.client('s3')
S3_BUCKET = 'ounass-csv-upload-files'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

@app.route('/health')
def health():
    return jsonify(status='UP'), 200


@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'message': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'message': 'No selected file'}, 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        upload_to_s3(file_path)
        return process_file(file_path)

@api_bp.route('/list-files')
def list_files():
    files = list_files_from_s3()
    return render_template('list_files.html', files=files)

@api_bp.route('/view-file/<filename>')
def view_file(filename):
    file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
    df = pd.read_csv(file_obj['Body'])
    df.columns = ["SKU no", "Description", "Price (د.إ)"]
    return render_template('result.html', data=df.to_html(index=False, classes='table table-striped'))

def upload_to_s3(file_path):
    s3_client.upload_file(file_path, S3_BUCKET, os.path.basename(file_path))

def list_files_from_s3():
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files

# Create a Blueprint for the main application routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/result')
def result():
    return render_template('result.html')

def process_file(file_path):
    df = pd.read_csv(file_path)
    df.columns = ["SKU no", "Description", "Price (د.إ)"]
    return render_template('result.html', data=df.to_html(index=False, classes='table table-striped'))

# Register the Blueprints with the app
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
