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

def generate_presigned_url(bucket_name, s3_key, expiration=os.getenv('S3_URL_EXPIRATION')):
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
        print("No credentials provided to access S3.")
        return False
    except ClientError as e:
        print(f"Client error during S3 upload: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during S3 upload: {e}")
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
        file_hash = existing_files.split('/')[0]
        file_name = existing_files.split('/')[-1]
        presigned_url_existing_files = generate_presigned_url(S3_BUCKET, existing_files)
        return jsonify({
            "message": "File already exists with the same content",
            "presigned_url": presigned_url_existing_files,
            "file_hash": file_hash,
            "file_name": file_name,
        }), 200

    # Upload file to S3
    if upload_to_s3(file, S3_BUCKET, s3_key):
        presigned_url = generate_presigned_url(S3_BUCKET, s3_key)

        return jsonify({
            "message": "File uploaded successfully",
            "presigned_url": presigned_url,
            "file_hash": file_hash,
            "file_name": file.filename
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
                                # Extract file hash (assumed to be the first part of the key)
                file_key = file['Key']
                file_hash = file_key.split('/')[0]
                file_name = file_key.split('/')[-1]
                matching_files.append({
                    "file_name": file_name,
                    "file_hash": file_hash,
                    "presigned_url": generate_presigned_url(S3_BUCKET, file_key)
                })

    if not matching_files:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"message": f"We have {len(matching_files)} file(s) found", "matching_files": matching_files}), 200

# Route to delete a file
@app.route('/files/<file_hash>', methods=['DELETE'])
def delete_file(file_hash):

    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=file_hash,MaxKeys=1)
    if 'Contents' in response:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=response['Contents'][0]['Key'])
        return jsonify({"message": "File deleted successfully",
                        "file_hash":file_hash,
                        "path":response['Contents'][0]['Key']
                        }), 200
    else:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({
        "status": "healthy",
        "message": "The service is up and running"
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
