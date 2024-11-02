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
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from api.app import app


@pytest.mark.anyio
class TestNoExpenses:
    async def test_expense_bar_no_expenses(self, async_client_auth: AsyncClient):
        # Fetch a bar chart for a date range with no expenses
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": 30},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"

    async def test_expense_pie_no_expenses(self, async_client_auth: AsyncClient):
        # Fetch a pie chart for a date range with no expenses
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": 30},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"


@pytest.mark.anyio
class TestAddExpensesForAnalytics:
    async def test_add_expenses(self, async_client_auth: AsyncClient):
        # Adding sample expenses to test analytics
        expenses = [
            {
                "amount": 100.0,
                "currency": "USD",
                "category": "Food",
                "description": "Groceries",
                "account_name": "Checking",
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
            },
            {
                "amount": 50.0,
                "currency": "USD",
                "category": "Transport",
                "description": "Bus fare",
                "account_name": "Checking",
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
            },
            {
                "amount": 200.0,
                "currency": "USD",
                "category": "Utilities",
                "description": "Concert ticket",
                "account_name": "Checking",
                "date": (datetime.now() - timedelta(days=3)).isoformat(),
            },
        ]
        for expense in expenses:
            response = await async_client_auth.post("/expenses/", json=expense)
            assert response.status_code == 200, response.json()
            assert response.json()["message"] == "Expense added successfully"


@pytest.mark.anyio
class TestAnalyticsBarChart:
    async def test_expense_bar_success(self, async_client_auth: AsyncClient):
        # Fetch a bar chart with a valid x_days and valid token
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": 7},
        )
        assert response.status_code == 200, response.json()
        assert "Total Expenses per Day" in response.text
        assert "<img src=" in response.text

    async def test_expense_bar_large_date_range(self, async_client_auth: AsyncClient):
        # Fetch a bar chart with a large x_days value
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": 365},
        )
        assert response.status_code == 200, response.json()
        assert "Total Expenses per Day" in response.text


@pytest.mark.anyio
class TestAnalyticsPieChart:
    async def test_expense_pie_success(self, async_client_auth: AsyncClient):
        # Fetch a pie chart with valid x_days and valid token
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": 7},
        )
        assert response.status_code == 200, response.json()
        assert "Expense Distribution by Category" in response.text
        assert "<img src=" in response.text

    async def test_expense_pie_large_date_range(self, async_client_auth: AsyncClient):
        # Fetch a pie chart with a large x_days value
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": 365},
        )
        assert response.status_code == 200, response.json()
        assert "Expense Distribution by Category" in response.text


@pytest.mark.anyio
class TestAnalyticsEdgeCases:
    async def test_expense_bar_zero_days(self, async_client_auth: AsyncClient):
        # Fetch bar chart with x_days set to 0
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": 0},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"

    async def test_expense_pie_zero_days(self, async_client_auth: AsyncClient):
        # Fetch pie chart with x_days set to 0
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": 0},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"

    async def test_expense_bar_negative_days(self, async_client_auth: AsyncClient):
        # Fetch bar chart with x_days set to a negative value
        response = await async_client_auth.get(
            "/analytics/expense/bar",
            params={"x_days": -5},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"

    async def test_expense_pie_negative_days(self, async_client_auth: AsyncClient):
        # Fetch pie chart with x_days set to a negative value
        response = await async_client_auth.get(
            "/analytics/expense/pie",
            params={"x_days": -5},
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "No expenses found for the specified period"
