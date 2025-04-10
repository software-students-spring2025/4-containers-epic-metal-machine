import sys
import os
import pytest
from unittest.mock import MagicMock, patch
sys.path.append(os.path.abspath("./web-app"))
import app
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
import io

#  package for creating mock mongoDB databases
@pytest.fixture
def mongoDB_simulation():
    """Simulates mongoDB database"""
    users = MagicMock()
    entries = MagicMock()
    db = MagicMock()
    db.__getitem__.side_effect = lambda x: users if x == "users" else entries
    with patch('app.DB', db), \
            patch('app.COLLECTION', entries):
        yield (users, entries)


@pytest.fixture
def client():
    """Setup test Flask app"""
    app.app.config["TESTING"] = True
    app.app.config["WTF_CSRF_ENABLED"] = False
    with app.app.test_client() as test_client:
        yield test_client


# Create a simulated user
@pytest.fixture
def user_simulation(client, mongoDB_simulation):
    """Creates a simulated user"""
    users, _ = mongoDB_simulation
    user_id = ObjectId()
    password = generate_password_hash("testpassword")
    mock_user = {
        "_id": user_id,
        "username": "testuser",
        "password": password
    }
    # Mock loader to return user object directly
    with patch('app.check_password_hash', return_value=True), \
            patch('app.load_user', return_value=app.User(user_id, "testuser", password)), \
            patch('app.flash') as mock_flash:
        users.find_one.return_value = mock_user
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpassword"
        }, follow_redirects=True)
        mock_flash.assert_called_with("Logged in successfully.")
        return client


def test_signup(client, mongoDB_simulation):
    """Tests creating a new user profile"""
    users, _ = mongoDB_simulation
    # mock the generated password
    with patch('app.generate_password_hash', return_value="pbkdf2:sha256:test_hash"):
        response = client.post("/signup", data={
            "username": "newuser",
            "password": "newpassword",
            "email": "user@example.com"
        }, follow_redirects=True)
        assert response.status_code == 200
    # test if insert called correctly
    users.insert_one.assert_called_once()
    args = users.insert_one.call_args[0][0]
    assert "password" in args


def test_login(client, mongoDB_simulation):
    """
    Tests logging in
    """
    users, _ = mongoDB_simulation
    # Successful login attempt
    user_id = ObjectId()
    password = generate_password_hash("testpassword")
    user = {
        "_id": user_id,
        "username": "testuser",
        "password": password
    }
    users.find_one.return_value = user
    with patch('app.check_password_hash', return_value=True), \
            patch('app.flash') as mock_flash:
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpassword"
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_flash.assert_called_with("Logged in successfully.")
    # 2. Test failed login
    users.find_one.return_value = None
    response = client.post("/login", data={
        "username": "wronguser",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    # 3. Test access to protected route without proper authentication
    response = client.get("/", follow_redirects=True)
    assert b"Login" in response.data


@patch('app.requests.post')
def test_upload(post, user_simulation):
    """
    Image upload test
    """
    post.return_value = MagicMock(status_code=200)
    # Test with valid image file
    test_file = (io.BytesIO(b"test image content"), "test.png")
    response = user_simulation.post(
        "/upload",
        data={
            "image": test_file
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert response.status_code == 200
    assert post.called
    # Test with no file
    post.reset_mock()
    response = user_simulation.post("/upload", follow_redirects=True)
    assert b"Error: No image uploaded" in response.data
    assert not post.called
    # Test with invalid file type
    post.reset_mock()
    test_file = (io.BytesIO(b"test document content"), "test.pdf")
    response = user_simulation.post(
        "/upload",
        data={"image": test_file},
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert b"Invalid file type" in response.data
    assert not post.called