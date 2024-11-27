import pytest
from httpx import AsyncClient

from api.app import app


@pytest.mark.anyio
class TestRoutes:
    async def test_root_redirect(self, async_client: AsyncClient):
        response = await async_client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    async def test_signup_page(self, async_client: AsyncClient):
        response = await async_client.get("/signup")
        assert response.status_code == 200

    async def test_login_page(self, async_client: AsyncClient):
        response = await async_client.get("/login")
        assert response.status_code == 200
        assert "<title>Login</title>" in response.text

    async def test_landing_page_no_token(self, async_client: AsyncClient):
        response = await async_client.get("/landing")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    async def test_categories_page_no_token(self, async_client: AsyncClient):
        response = await async_client.get("/categories")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    async def test_expenses_page_no_token(self, async_client: AsyncClient):
        response = await async_client.get("/expenses")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    async def test_barchart_page_no_token(self, async_client: AsyncClient):
        response = await async_client.get("/barchart")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    async def test_piechart_page_no_token(self, async_client: AsyncClient):
        response = await async_client.get("/piechart")
        assert response.status_code == 302
        assert response.headers["location"] == "/login"


@pytest.mark.anyio
class TestProtectedRoutes:
    async def test_landing_page_with_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/landing", cookies={"access_token": "invalidtoken"}
        )
        assert response.status_code == 302

    async def test_categories_page_with_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/categories", cookies={"access_token": "invalidtoken"}
        )
        assert response.status_code == 302

    async def test_expenses_page_with_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/expenses", cookies={"access_token": "invalidtoken"}
        )
        assert response.status_code == 302

    async def test_barchart_page_with_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/barchart", cookies={"access_token": "invalidtoken"}
        )
        assert response.status_code == 302

    async def test_piechart_page_with_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/piechart", cookies={"access_token": "invalidtoken"}
        )
        assert response.status_code == 302
