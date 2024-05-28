from test_task.services.auth.auth import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_hashed_password,
    verify_password,
)


def test_get_hashed_password() -> None:
    """Tests get_hashed_password function."""
    password = "testpassword"
    hashed_password = get_hashed_password(password)
    assert hashed_password != password


def test_verify_password() -> None:
    """Tests verify_password function."""
    password = "testpassword"
    hashed_password = get_hashed_password(password)
    assert verify_password(password, hashed_password)


def test_create_access_token() -> None:
    """Tests create_access_token function."""
    data = {"email": "test@example.com", "username": "testuser", "user_id": 1}
    token = create_access_token(data)  # type: ignore
    assert token is not None


def test_decode_access_token() -> None:
    """Tests decode_access_token function."""
    data = {"email": "test@example.com", "username": "testuser", "user_id": 1}
    token = create_access_token(data)  # type: ignore
    decoded_data = decode_access_token(token)
    assert decoded_data.email == data["email"]
    assert decoded_data.username == data["username"]
    assert decoded_data.user_id == data["user_id"]


def test_create_refresh_token() -> None:
    """Tests create_refresh_token function."""
    data = {"email": "test@example.com", "username": "testuser", "user_id": 1}
    token = create_refresh_token(data)  # type: ignore
    assert token is not None


def test_decode_refresh_token() -> None:
    """Tests decode_refresh_token function."""
    data = {"email": "test@example.com", "username": "testuser", "user_id": 1}
    token = create_refresh_token(data)  # type: ignore
    decoded_data = decode_refresh_token(token)
    assert decoded_data.email == data["email"]
    assert decoded_data.username == data["username"]
    assert decoded_data.user_id == data["user_id"]
