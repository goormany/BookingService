
from src.utils.enums.user_roles import UserRoleEnum


async def test_get_me(employee_ac):
    response = await employee_ac.get(
        "/api/v1/users/me"
    )
    assert response.status_code == 200
    assert response.json()["username"] == "employee"

async def test_get_all_users_as_admin(admin_ac):
    response = await admin_ac.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_get_all_users_as_employee(employee_ac):
    response = await employee_ac.get("/api/v1/users/")
    assert response.status_code == 403

async def test_get_user_by_id_as_admin(admin_ac):
    response = await admin_ac.get("/api/v1/users/1")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == 1

async def test_get_user_by_id_as_employee(employee_ac):
    response = await employee_ac.get("/api/v1/users/1")
    assert response.status_code == 403

async def test_get_user_not_found(admin_ac):
    response = await admin_ac.get("/api/v1/users/1000000")
    assert response.status_code == 404

async def test_change_role_as_admin(admin_ac):
    username = "test_change_role_as_adm"
    password = "password"
    response1 = await admin_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]
    user_role = user["role"]
    
    response2 = await admin_ac.patch(
        f"/api/v1/users/{user_id}",
        json={
            "role": UserRoleEnum.ADMIN
        }
    )
    assert response2.status_code == 200
    new_user = response2.json()
    
    assert user_id == new_user["id"]
    assert user_role != new_user["role"]
    
async def test_change_role_as_employee(employee_ac):
    username = "test_change_role_as_employee"
    password = "password"
    response1 = await employee_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]

    response2 = await employee_ac.patch(
        f"/api/v1/users/{user_id}",
        json={
            "role": UserRoleEnum.ADMIN
        }
    )
    assert response2.status_code == 403


async def test_soft_delete_user_as_admin(admin_ac):
    username = "test_soft_delete_user_as_admin"
    response1 = await admin_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "password"
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]
    user_is_active = user["is_active"]
    assert user_is_active is True
    
    response2 = await admin_ac.delete(
        f"/api/v1/users/{user_id}"
    )
    assert response2.status_code == 200
    new_user = response2.json()
    
    assert user_is_active != new_user["is_active"]
    assert new_user["is_active"] is False


async def test_soft_delete_user_as_employee(employee_ac):
    username = "test_soft_delete_user_as_employee"
    response1 = await employee_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "password"
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]
    user_is_active = user["is_active"]
    assert user_is_active is True
    
    response2 = await employee_ac.delete(
        f"/api/v1/users/{user_id}"
    )
    assert response2.status_code == 403
    
    
    


async def test_hard_delete_user_as_admin(admin_ac):
    username = "test_hard_delete_user"
    response1 = await admin_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "password"
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]
    
    response2 = await admin_ac.delete(
        f"/api/v1/users/{user_id}/hard"
    )
    assert response2.status_code == 200


async def test_hard_delete_user_as_employee(employee_ac):
    username = "test_hard_delete_user"
    response1 = await employee_ac.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "password"
        }
    )
    assert response1.status_code == 201
    user = response1.json()
    user_id = user["id"]
    
    response2 = await employee_ac.delete(
        f"/api/v1/users/{user_id}/hard"
    )
    assert response2.status_code == 403