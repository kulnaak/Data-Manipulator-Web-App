from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Load the file into a DataFrame
    if filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    # Respond with the columns available in the uploaded file
    return jsonify({"columns": df.columns.tolist(), "filename": filename})

@app.route('/process', methods=['POST'])
def process_file():
    data = request.get_json()
    filename = data.get('filename')
    columns = data.get('columns', [])
    transformations = data.get('transformations', {})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Load the file into a DataFrame
    if filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    # Select the specified columns
    if columns:
        df = df[columns]

    # Apply transformations (placeholder for transformation logic)
    # Example: Multiply a column by a factor
    for column, operation in transformations.items():
        if operation['type'] == 'multiply' and column in df.columns:
            df[column] *= operation['value']

    # Save the processed file
    processed_filename = f"processed_{filename}"
    processed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    df.to_csv(processed_file_path, index=False)

    return send_file(processed_file_path, as_attachment=True, download_name=processed_filename)

if __name__ == '__main__':
    app.run(debug=True)
