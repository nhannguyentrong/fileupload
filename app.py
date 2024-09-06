from flask import Flask, request, jsonify
import os
import hashlib

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def calculate_file_hash(file):
    file_hash = hashlib.md5()
    while chunk := file.read(8192):
        file_hash.update(chunk)
    file.seek(0)  # Reset file pointer after reading
    return file_hash.hexdigest()

# Route to upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Calculate file hash
    file_hash = calculate_file_hash(file)

    hash_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash)
    
    if os.path.exists(hash_folder_path):
        existing_files = os.listdir(hash_folder_path)
        existing_file_paths = [os.path.join(hash_folder_path, f) for f in existing_files]
        return jsonify({
            "message": "File already exists with the same content",
            "existing_files": existing_file_paths
        }), 200

    if not os.path.exists(hash_folder_path):
        os.makedirs(hash_folder_path)

    saved_file_path = os.path.join(hash_folder_path, file.filename)
    
    file.save(saved_file_path)
    
    return jsonify({
        "message": "File uploaded successfully",
        "file_path": saved_file_path
    }), 201


@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    matching_files = []

    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        # Look for partial matches
        for file in files:
            if filename in file: 
                file_path = os.path.join(root, file)
                matching_files.append(file_path)

    if not matching_files:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"message": "File(s) found", "matching_files": matching_files}), 200


@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    matching_paths = []

    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        if filename in files:
            file_path = os.path.join(root, filename)
            matching_paths.append(file_path)

    if not matching_paths:
        return jsonify({"error": "File not found"}), 404

    deleted_folders = []
    for file_path in matching_paths:
        folder_path = os.path.dirname(file_path)
        
        os.remove(file_path)
        
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
            deleted_folders.append(folder_path)

    return jsonify({
        "message": f"{len(matching_paths)} file(s) deleted successfully",
        "deleted_files": matching_paths,
        "deleted_folders": deleted_folders
    }), 200


if __name__ == '__main__':
    app.run(debug=True)