from datetime import timedelta

from src.utils.enums.user_roles import UserRoleEnum
from src.services.auth import AuthServices


async def test_register_success(ac):
    username = "test_username"
    password = "password"
    
    response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 201
    user = response.json()
    assert user["role"] == UserRoleEnum.EMPLOYEE.value
    assert user["username"] == username

async def test_register_duplicate_username(ac):
    username = "test_username"
    password = "password"
    
    response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 409
    
async def test_success_login(ac):
    username = "test_login_user"
    password = "test_password"
    
    register_response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    
    response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    
    assert response.status_code == 200
    tokens = response.json()
    assert tokens["token_type"] == "bearer"
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    assert access_token != refresh_token
    
    access_payload = AuthServices.decode_access_token(access_token)
    assert access_payload.sub == str(user_id)
    
    refresh_payload = AuthServices.decode_access_token(refresh_token)
    assert refresh_payload.sub == str(user_id)

async def test_login_wrong_password(ac):
    response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "notadmin"
        }
    )
    
    assert response.status_code == 401

async def test_login_nonexistent_user(ac):
    response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": "not_exist_username",
            "password": "password"
        }
    )
    assert response.status_code == 401

async def test_refresh_token_success(ac):
    username = "test_refresh_user"
    password = "test_password"
    
    register_response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    
    login_response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    assert login_response.status_code == 200
    old_tokens = login_response.json()
    old_refresh_token = old_tokens["refresh_token"]
    
    refresh_response = await ac.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )
    
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["token_type"] == "bearer"
    
    new_access_payload = AuthServices.decode_access_token(new_tokens["access_token"])
    assert new_access_payload.sub == str(user_id)
    
    new_refresh_payload = AuthServices.decode_access_token(new_tokens["refresh_token"])
    assert new_refresh_payload.sub == str(user_id)

async def test_refresh_token_expired(ac):
    username = "test_refresh_expired_user"
    password = "test_password"
    
    register_response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    
    expired_refresh_token = AuthServices.create_access_token(
        str(user_id),
        timedelta(seconds=-1)
    )
    
    response = await ac.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": expired_refresh_token
        }
    )
    
    assert response.status_code == 401


async def test_refresh_token_invalid(ac):
    response = await ac.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid_token"
        }
    )
    assert response.status_code == 401


async def test_register_empty_username(ac):
    response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": "",
            "password": "password123"
        }
    )
    assert response.status_code == 422


async def test_register_short_password(ac):
    response = await ac.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_{hash('short')}",
            "password": "123"
        }
    )
    assert response.status_code == 422


async def test_access_protected_endpoint_without_token(ac):
    response = await ac.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_access_protected_endpoint_with_invalid_token(ac):
    response = await ac.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


async def test_login_with_empty_username(ac):
    response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": "",
            "password": "password"
        }
    )
    assert response.status_code == 422


async def test_login_with_empty_password(ac):
    response = await ac.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": ""
        }
    )
    assert response.status_code == 422
