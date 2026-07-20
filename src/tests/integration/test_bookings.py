from datetime import date, timedelta


async def test_create_booking_as_employee(admin_ac, employee_ac):
    name = "test_booking_room"
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
    response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert response.status_code == 201
    booking = response.json()
    assert booking["room_id"] == room_id
    assert booking["start_time"] == "10:00:00Z"
    assert booking["end_time"] == "11:00:00Z"
    assert booking["status"] == "ACTIVE"


async def test_create_booking_conflict(admin_ac, employee_ac):
    name = "test_booking_conflict_room"
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
    
    response1 = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert response1.status_code == 201
    
    response2 = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert response2.status_code == 409


async def test_cancel_my_booking(admin_ac, employee_ac):
    name = "test_cancel_my_booking_room"
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
    create_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "12:00",
            "end_time": "13:00"
        }
    )
    assert create_response.status_code == 201
    booking_id = create_response.json()["id"]
    
    cancel_response = await employee_ac.delete(
        f"/api/v1/bookings/my/{booking_id}"
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"


async def test_cancel_my_booking_not_found(employee_ac):
    response = await employee_ac.delete("/api/v1/bookings/my/99999")
    assert response.status_code == 404


async def test_get_my_bookings(admin_ac, employee_ac):
    name = "test_get_my_bookings_room"
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
    create_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "14:00",
            "end_time": "15:00"
        }
    )
    assert create_response.status_code == 201
    
    response = await employee_ac.get("/api/v1/bookings/my")
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) >= 1


async def test_get_all_bookings_as_admin(admin_ac, employee_ac):
    name = "test_get_all_bookings_room"
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
    create_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "15:00",
            "end_time": "16:00"
        }
    )
    assert create_response.status_code == 201
    
    response = await admin_ac.get(
        f"/api/v1/bookings/?date={booking_date}"
    )
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) >= 1


async def test_get_all_bookings_as_employee(employee_ac):
    booking_date = date.today().isoformat()
    response = await employee_ac.get(
        f"/api/v1/bookings/?date={booking_date}"
    )
    assert response.status_code == 403


async def test_get_availability(admin_ac, employee_ac):
    name = "test_availability_room"
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
    response = await employee_ac.get(
        f"/api/v1/bookings/availability?date={booking_date}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == booking_date
    assert isinstance(data["rooms"], list)
    assert len(data["rooms"]) >= 1


async def test_get_availability_by_room(admin_ac, employee_ac):
    name = "test_availability_by_room"
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
    response = await employee_ac.get(
        f"/api/v1/bookings/availability/{room_id}?date={booking_date}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["room_id"] == room_id
    assert isinstance(data["slots"], list)


async def test_create_booking_nonexistent_room(employee_ac):
    booking_date = date.today().isoformat()
    response = await employee_ac.post(
        "/api/v1/bookings/99999",
        json={
            "booking_date": booking_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert response.status_code == 404


async def test_create_booking_past_date(admin_ac, employee_ac):
    name = "test_booking_past_date_room"
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
    
    past_date = (date.today() - timedelta(days=1)).isoformat()
    response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": past_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    assert response.status_code == 422


async def test_cancel_others_booking(admin_ac, employee_ac):
    name = "test_cancel_others_booking_room"
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
    create_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "12:00",
            "end_time": "13:00"
        }
    )
    assert create_response.status_code == 201
    booking_id = create_response.json()["id"]
    
    cancel_response = await admin_ac.delete(
        f"/api/v1/bookings/my/{booking_id}"
    )
    assert cancel_response.status_code == 404


async def test_get_booking_by_id(admin_ac, employee_ac):
    name = "test_get_booking_by_id_room"
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
    create_response = await employee_ac.post(
        f"/api/v1/bookings/{room_id}",
        json={
            "booking_date": booking_date,
            "start_time": "14:00",
            "end_time": "15:00"
        }
    )
    assert create_response.status_code == 201
    booking_id = create_response.json()["id"]
    
    response = await admin_ac.get(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


async def test_get_booking_not_found(employee_ac):
    response = await employee_ac.get("/api/v1/bookings/99999")
    assert response.status_code == 403
