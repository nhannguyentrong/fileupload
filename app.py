from flask import Flask, request, jsonify
import os
import hashlib
import boto3
from dotenv import load_dotenv

from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv()

app = Flask(__name__)

# S3 Configuration
S3_BUCKET = os.getenv('S3_BUCKET_NAME')

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION') )

def generate_presigned_url(bucket_name, s3_key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': s3_key},
                                                    ExpiresIn=expiration)
        return response
    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

def calculate_file_hash(file):
    file_hash = hashlib.md5()
    while chunk := file.read(8192):
        file_hash.update(chunk)
    file.seek(0) 
    return file_hash.hexdigest()

def upload_to_s3(file, bucket, s3_key):
    try:
        s3_client.upload_fileobj(file, bucket, s3_key)
        return True
    except NoCredentialsError:
        return False

def file_exists_in_s3(bucket, prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
        if 'Contents' in response:
            return True
        else:
            return False
    except ClientError as e:
        return False

def list_s3_files(bucket, prefix):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        return response['Contents'][0]['Key']
    return []

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

    s3_folder = file_hash
    s3_key = f"{s3_folder}/{file.filename}"

    if file_exists_in_s3(S3_BUCKET, s3_folder):
        existing_files = list_s3_files(S3_BUCKET, s3_folder)
        presigned_url_existing_files = generate_presigned_url(S3_BUCKET, existing_files)
        return jsonify({
            "message": "File already exists with the same content",
            "existing_files": presigned_url_existing_files 
        }), 200

    # Upload file to S3
    if upload_to_s3(file, S3_BUCKET, s3_key):
        presigned_url = generate_presigned_url(S3_BUCKET, s3_key)

        return jsonify({
            "message": "File uploaded successfully",
            "file_path": presigned_url 
        }), 201
    else:
        return jsonify({"error": "File upload failed"}), 500

# Route to retrieve a file (partial filename match)
@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    matching_files = []
    # Traverse S3 and look for partial matches in filenames
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    if 'Contents' in response:
        for file in response['Contents']:
            if filename in file['Key']:
                matching_files.append(generate_presigned_url(S3_BUCKET, file['Key']))

    if not matching_files:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"message": f"We have {len(matching_files)} file(s) found", "matching_files": matching_files}), 200

# Route to delete a file
@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    matching_paths = []
    deleted_files = []
    deleted_folders = []

    # List all objects in the S3 bucket
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    if 'Contents' in response:
        for obj in response['Contents']:
            if filename in obj['Key']:
                matching_paths.append(obj['Key'])

    if not matching_paths:
        return jsonify({"error": "File not found"}), 404

    # Delete matching files and their folders
    for file_path in matching_paths:
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=file_path)
            deleted_files.append(file_path)

            # Extract folder from the file path (hash)
            folder_path = file_path.rsplit('/', 1)[0]
            # Check if the folder is empty
            remaining_files = list_s3_files(S3_BUCKET, folder_path)
            if len(remaining_files) == 0:
                deleted_folders.append(folder_path)
        except ClientError:
            return jsonify({"error": "Error deleting file"}), 500

    return jsonify({
        "message": f"{len(deleted_files)} file(s) deleted successfully",
        "deleted_files": deleted_files,
        "deleted_folders": deleted_folders
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
