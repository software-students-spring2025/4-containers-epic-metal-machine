from io import BytesIO
import os
import pytest
from unittest.mock import MagicMock, patch
import machine_learning_client.client as client
from PIL import Image
import numpy as np


@pytest.fixture
def test_client():
    """Setup test Flask app"""
    client.app.config["TESTING"] = True
    client.app.config["UPLOAD_FOLDER"] = "test_uploads"
    os.makedirs(client.app.config["UPLOAD_FOLDER"], exist_ok=True)
    with client.app.test_client() as test_client:
        yield test_client

@pytest.fixture
def mongodb_simulation():
    """Simulates mongoDB database for client tests"""
    db = MagicMock()
    return db

def test_upload(test_client):
    # Simulate image file
    data = BytesIO()
    img = Image.new('RGB', (100, 30), color='white')
    img.save(data, format='PNG')
    data.seek(0)
    with patch('machine_learning_client.client.collection.insert_one') as insert:
        response = test_client.post('/upload', data={
            'file': (data, 'test.png'),
            'id': 'test_user_123'
        }, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'successful'
        insert.assert_called_once()


@patch('machine_learning_client.client.pytesseract.image_to_data')
@patch('machine_learning_client.client.cv2.imread')
@patch('machine_learning_client.client.cv2.cvtColor')
@patch('machine_learning_client.client.cv2.threshold')
@patch('machine_learning_client.client.Image.fromarray')
def test_confidence(fromarray, threshold, cvtcolor,
                    imread, image_to_data, test_client, mongodb_simulation):
    """Tests Confidence filtering"""
    # Simulate image
    image = np.ones((300, 400), dtype=np.uint8) * 255
    imread.return_value = image
    cvtcolor.return_value = image
    threshold.return_value = (None, image)
    pil_image = MagicMock()
    fromarray.return_value = pil_image
    # simulate pytesseract OCR output with different confidence scores
    mock_ocr_data = {
        'text': ['High', 'confidence', 'word', 'Low', 'confidence', 'word'],
        'conf': [90, 85, 80, 30, 25, 20],
        'line_num': [1, 1, 1, 2, 2, 2]
    }
    image_to_data.return_value = mock_ocr_data
    test_file = BytesIO(b"test file content")
    # Simulated MongoDB insert
    with patch('machine_learning_client.client.collection.insert_one') as insert_mock:
        response = test_client.post(
            '/upload',
            data={
                'id': 'test_user_id',
                'file': (test_file, 'test.png', 'image/png')
            },
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        insert_mock.assert_called_once()
        # Test text filtering
        call_args = insert_mock.call_args[0][0]
        assert "High confidence word" in call_args['text']
        assert "Low confidence word" not in call_args['text']