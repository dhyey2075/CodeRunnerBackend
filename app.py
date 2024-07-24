import os
import subprocess
from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
OUTPUT_FILE = 'output.txt'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'code_file' not in request.files or 'input_file' not in request.files:
        return 'No file part', 400
    
    code_file = request.files['code_file']
    input_file = request.files['input_file']
    
    if code_file.filename == '' or input_file.filename == '':
        return 'No selected file', 400
    
    code_file_path = os.path.join(UPLOAD_FOLDER, code_file.filename)
    input_file_path = os.path.join(UPLOAD_FOLDER, 'input.txt')

    files = os.listdir(UPLOAD_FOLDER)
    for f in files:
        delPath = os.path.join(UPLOAD_FOLDER, f)
        os.remove(delPath)
    
    code_file.save(code_file_path)
    input_file.save(input_file_path)
    
    file_extension = os.path.splitext(code_file.filename)[1]

    # Determine the command to run based on file type
    if file_extension == '.py':
        command = ['python', code_file_path]
    elif file_extension == '.c':
        exe_file_path = code_file_path.rsplit('.', 1)[0]
        compile_result = subprocess.run(['gcc', code_file_path, '-o', exe_file_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Compilation failed: {compile_result.stderr}", 400
        command = [exe_file_path]
    elif file_extension == '.cpp':
        exe_file_path = code_file_path.rsplit('.', 1)[0]
        compile_result = subprocess.run(['g++', code_file_path, '-o', exe_file_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Compilation failed: {compile_result.stderr}", 400
        command = [exe_file_path]
    elif file_extension == '.js':
        command = ['node', code_file_path]
    else:
        return 'Unsupported file type', 400

    # Run the code file with input.txt
    with open(input_file_path, 'r') as input_file, open(OUTPUT_FILE, 'w') as output_file:
        run_result = subprocess.run(command, stdin=input_file, stdout=output_file, stderr=subprocess.PIPE, text=True)
    
    if run_result.returncode != 0:
        return f"Execution failed: {run_result.stderr}", 400
    
    return 'Files processed successfully.', 200

@app.route('/output')
def get_output():
    if not os.path.exists(OUTPUT_FILE):
        return 'Output file not found', 404

    return send_file(OUTPUT_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
