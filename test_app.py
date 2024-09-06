import os
import unittest
import hashlib
from io import BytesIO
from app import app

class FlaskFileApiTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()  # Create a test client
        cls.upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(cls.upload_folder):
            os.makedirs(cls.upload_folder)

    @classmethod
    def tearDownClass(cls):
        # Remove upload folder after tests
        if os.path.exists(cls.upload_folder):
            for root, dirs, files in os.walk(cls.upload_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(cls.upload_folder)

    def calculate_file_hash(self, file_content):
        file_hash = hashlib.md5(file_content).hexdigest()
        return file_hash

    def test_upload_file(self):
        """Test uploading a file and check if it is stored properly."""
        file_data = b"Hello, World!"
        response = self.client.post('/upload', data={
            'file': (BytesIO(file_data), 'testfile.txt')
        })

        # Check if the response is successful
        self.assertEqual(response.status_code, 201)
        
        # Calculate the hash and check the file path
        file_hash = self.calculate_file_hash(file_data)
        expected_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash, 'testfile.txt')

        # Check if the file was saved correctly
        self.assertTrue(os.path.exists(expected_file_path))

    def test_upload_duplicate_file(self):
        """Test uploading the same file with different names but same content."""
        file_data = b"Duplicate content!"
        self.client.post('/upload', data={
            'file': (BytesIO(file_data), 'firstfile.txt')
        })
        
        # Try uploading the same file with a different name
        response = self.client.post('/upload', data={
            'file': (BytesIO(file_data), 'secondfile.txt')
        })
        
        # The response should indicate that the file already exists
        self.assertEqual(response.status_code, 200)
        self.assertIn("File already exists with the same content", response.get_json()['message'])

    def test_get_existing_file_with_partial_match(self):
        """Test retrieving a file with a partial filename match."""
        file_data = b"Retrieve me!"
        self.client.post('/upload', data={
            'file': (BytesIO(file_data), 'docker-compose.yml')
        })
        
        # Try retrieving using a partial filename
        response = self.client.get('/files/compose')
        self.assertEqual(response.status_code, 200)
        self.assertIn('docker-compose.yml', response.get_json()['matching_files'][0])

    def test_get_file_not_found(self):
        """Test retrieving a non-existing file."""
        response = self.client.get('/files/nonexistentfile')
        self.assertEqual(response.status_code, 404)
        self.assertIn("File not found", response.get_json()['error'])

    def test_delete_file(self):
        """Test deleting an existing file."""
        file_data = b"Delete me!"
        self.client.post('/upload', data={
            'file': (BytesIO(file_data), 'todelete.txt')
        })
        
        # Try deleting the file
        response = self.client.delete('/files/todelete.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted_files', response.get_json())

    def test_delete_file_not_found(self):
        """Test deleting a non-existing file."""
        response = self.client.delete('/files/nofile')
        self.assertEqual(response.status_code, 404)
        self.assertIn("File not found", response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
