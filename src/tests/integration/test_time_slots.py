import pytest


async def test_create_slot_as_admin(admin_ac):
    name = "test_create_slot_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    response = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "09:00",
            "end": "10:00"
        }
    )
    assert response.status_code == 201
    slot = response.json()
    assert slot["start"] == "09:00:00Z"
    assert slot["end"] == "10:00:00Z"
    assert slot["room_id"] == room_id


async def test_create_slot_as_employee(employee_ac):
    response = await employee_ac.post(
        "/api/v1/rooms/1/slots/",
        json={
            "start": "10:00",
            "end": "11:00"
        }
    )
    assert response.status_code == 403


async def test_create_slot_duplicate(admin_ac):
    name = "test_create_slot_duplicate_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    response1 = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "11:00",
            "end": "12:00"
        }
    )
    assert response1.status_code == 201
    
    response2 = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "11:00",
            "end": "12:00"
        }
    )
    assert response2.status_code == 409


async def test_create_slot_invalid_time(admin_ac):
    name = "test_create_slot_invalid_time_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    response = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "12:00",
            "end": "11:00"
        }
    )
    assert response.status_code == 409


async def test_delete_slot_as_admin(admin_ac):
    name = "test_delete_slot_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    create_response = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "13:00",
            "end": "14:00"
        }
    )
    assert create_response.status_code == 201
    slot_id = create_response.json()["id"]
    
    delete_response = await admin_ac.delete(
        f"/api/v1/rooms/{room_id}/slots/{slot_id}"
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == slot_id


async def test_delete_slot_as_employee(admin_ac, employee_ac):
    name = "test_delete_slot_employee_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    create_response = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "14:00",
            "end": "15:00"
        }
    )
    assert create_response.status_code == 201
    slot_id = create_response.json()["id"]
    
    delete_response = await employee_ac.delete(
        f"/api/v1/rooms/{room_id}/slots/{slot_id}"
    )
    assert delete_response.status_code == 403


async def test_delete_slot_not_found(admin_ac):
    response = await admin_ac.delete("/api/v1/rooms/1/slots/99999")
    assert response.status_code == 404