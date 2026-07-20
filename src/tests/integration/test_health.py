async def test_health_check(ac):
    response = await ac.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

async def test_health_check_unauthorized(ac):
    response = await ac.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

async def test_health_check_authenticated(admin_ac):
    response = await admin_ac.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}