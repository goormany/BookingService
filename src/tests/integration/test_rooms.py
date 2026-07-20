import pytest


async def test_create_room_as_admin(admin_ac):
    name = "test_create_room_as_admin"
    response = await admin_ac.post("/api/v1/rooms/", json={"name": name})
    assert response.status_code == 201
    room = response.json()
    assert room["name"] == name
    assert room["description"] is None


async def test_create_room_as_employee(employee_ac):
    name = "test_create_room_as_employee"
    response = await employee_ac.post(
        "/api/v1/rooms/", json={"name": name, "description": "..."}
    )
    assert response.status_code == 403


@pytest.mark.parametrize("client", ["employee_ac", "admin_ac"])
async def test_get_all_rooms(client, request):
    client = request.getfixturevalue(client)

    response = await client.get("/api/v1/rooms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("client", ["employee_ac", "admin_ac"])
async def test_get_room_by_id(client, request):
    client = request.getfixturevalue(client)

    response = await client.get("/api/v1/rooms/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


async def test_update_room_as_admin(admin_ac):
    name = "test_update_room_as_admin"
    response1 = await admin_ac.post("/api/v1/rooms/", json={"name": name})
    assert response1.status_code == 201
    room = response1.json()
    room_id = room["id"]
    room_desc = room["description"]

    response2 = await admin_ac.patch(
        f"/api/v1/rooms/{room_id}", json={"description": "new_desc"}
    )
    assert response2.status_code == 200
    new_room_data = response2.json()

    assert new_room_data["id"] == room_id
    assert new_room_data["description"] is not None
    assert new_room_data["description"] != room_desc


async def test_update_room_as_employee(admin_ac, employee_ac):
    name = "test_update_room_as_employee"
    response1 = await admin_ac.post("/api/v1/rooms/", json={"name": name})
    assert response1.status_code == 201
    room = response1.json()
    room_id = room["id"]

    response2 = await employee_ac.patch(
        f"/api/v1/rooms/{room_id}", json={"description": "new_desc"}
    )
    assert response2.status_code == 403


async def test_delete_room_as_admin(admin_ac):
    name = "test_update_room_as_employee"
    response1 = await admin_ac.post("/api/v1/rooms/", json={"name": name})
    assert response1.status_code == 201
    room = response1.json()
    room_id = room["id"]

    response2 = await admin_ac.delete(f"/api/v1/rooms/{room_id}")
    assert response2.status_code == 200
    assert isinstance(response2.json(), dict)

    response3 = await admin_ac.get(f"/api/v1/rooms/{room_id}")
    assert response3.status_code == 404


async def test_delete_room_as_employee(admin_ac, employee_ac):
    name = "test_update_room_as_employee"
    response1 = await admin_ac.post("/api/v1/rooms/", json={"name": name})
    assert response1.status_code == 201
    room = response1.json()
    room_id = room["id"]

    response2 = await employee_ac.delete(f"/api/v1/rooms/{room_id}")
    assert response2.status_code == 403


async def test_get_room_not_found(employee_ac):
    response = await employee_ac.get("/api/v1/rooms/99999")
    assert response.status_code == 404


async def test_update_room_not_found(admin_ac):
    response = await admin_ac.patch(
        "/api/v1/rooms/99999", json={"description": "new_desc"}
    )
    assert response.status_code == 404


async def test_delete_room_not_found(admin_ac):
    response = await admin_ac.delete("/api/v1/rooms/99999")
    assert response.status_code == 404


async def test_create_room_without_name(admin_ac):
    response = await admin_ac.post("/api/v1/rooms/", json={})
    assert response.status_code == 422


async def test_get_rooms_unauthorized(ac):
    response = await ac.get("/api/v1/rooms/")
    assert response.status_code == 401
