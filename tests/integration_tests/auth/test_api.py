import pytest


@pytest.mark.parametrize("email, password, status_code", [
        ("test1@test1.com", "test1234", 200),
        ("test2@test2.com", "test1234", 200),
        ("test2@test2.com", "test1234", 400),
        ("abcde", "test1234", 422),
    ])
async def test_auth_flow(email: str, password: str, status_code: int, ac):
    #/auth/register
    resp_register = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )
    assert resp_register.status_code == status_code
    if status_code != 200:
        return

    #/auth/login
    resp_login = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert resp_login.status_code == status_code
    assert ac.cookies["access_token"]
    assert "access_token" in resp_login.json()

    #/auth/me
    resp_me = await ac.get("/auth/me")
    assert resp_me.status_code == status_code
    user = resp_me.json()
    assert user["email"] == email
    assert "id" in user
    assert "password" not in user
    assert "hashed_password" not in user

    #/auth/logout
    resp_logout = await ac.post("/auth/logout")
    assert resp_logout.status_code == status_code
    assert "access_token" not in ac.cookies
