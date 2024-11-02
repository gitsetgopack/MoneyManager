"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""
from asyncio import get_event_loop
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from api.app import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def async_client_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a user and log in to use for expenses tests
        await client.post(
            "/users/", json={"username": "testuser", "password": "testpassword"}
        )
        response = await client.post(
            "/users/token/", data={"username": "testuser", "password": "testpassword"}
        )
        token = response.json()["result"]["token"]
        client.headers.update({"token": token})

        account_response = await client.get("/accounts/")

        accounts = account_response.json()["accounts"]
        for account in accounts:
            if account["name"] == "Checking":
                account_id = account["_id"]
                # Update the balance of the Checking account
                await client.put(
                    f"/accounts/{account_id}",
                    json={"balance": 1000.0, "currency": "USD", "name": "Checking"},
                )

        yield client

        # Teardown: Delete the user after the tests in this module
        response = await client.delete("/users/")
        assert response.status_code == 200, response.json()
        assert (
            response.json()["message"] == "User deleted successfully"
        ), response.json()
