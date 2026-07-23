from src.utils.enums.redis_state import RedisStateEnum


async def test_health_check(ac):
    response = await ac.get("/api/v1/health/")
    
    redis_manager = ac._transport.app.state.redis_manager
    if redis_manager.state is RedisStateEnum.CONNECTED:
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    else:
        assert response.status_code == 500


async def test_health_check_authenticated(admin_ac):
    response = await admin_ac.get("/api/v1/health/")
    
    redis_manager = admin_ac._transport.app.state.redis_manager
    if redis_manager.state is RedisStateEnum.CONNECTED:
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    else:
        assert response.status_code == 500
