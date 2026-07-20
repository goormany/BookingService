from datetime import date


async def test_get_bookings_by_room_as_admin(admin_ac, employee_ac):
    name = "test_get_bookings_by_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    slot_response = await admin_ac.post(
        f"/api/v1/rooms/{room_id}/slots/",
        json={
            "start": "09:00",
            "end": "18:00"
        }
    )
    assert slot_response.status_code == 201
    
    booking_date = date.today().isoformat()
    booking_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert booking_response.status_code == 201
    
    response = await admin_ac.get(f"/api/v1/rooms/{room_id}/bookings")
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) >= 1


async def test_get_bookings_by_room_as_employee(admin_ac, employee_ac):
    name = "test_get_bookings_by_room_employee"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    response = await employee_ac.get(f"/api/v1/rooms/{room_id}/bookings")
    assert response.status_code == 403


async def test_get_bookings_by_room_not_found(admin_ac):
    response = await admin_ac.get("/api/v1/rooms/999999/bookings")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_bookings_empty_room(admin_ac):
    name = "test_get_bookings_empty_room"
    room_response = await admin_ac.post(
        "/api/v1/rooms/",
        json={
            "name": name
        }
    )
    assert room_response.status_code == 201
    room_id = room_response.json()["id"]
    
    response = await admin_ac.get(f"/api/v1/rooms/{room_id}/bookings")
    assert response.status_code == 200
    assert response.json() == []


async def test_rooms_pagination(admin_ac):
    name_prefix = "pagination_room"
    for i in range(25):
        await admin_ac.post(
            "/api/v1/rooms/",
            json={
                "name": f"{name_prefix}_{i}"
            }
        )
    
    response = await admin_ac.get("/api/v1/rooms/?page=2&per_page=10")
    assert response.status_code == 200
    rooms = response.json()
    assert isinstance(rooms, list)
    assert len(rooms) == 10
