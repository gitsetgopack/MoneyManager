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

import pytest
from httpx import AsyncClient

from api.app import app


@pytest.mark.anyio
class TestCategoryCreation:
    async def test_create_category(self, async_client_auth: AsyncClient):
        # Create a new category
        response = await async_client_auth.post(
            "/categories/", json={"name": "Entertainment", "monthly_budget": 150.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_duplicate_category(self, async_client_auth: AsyncClient):
        # Try creating the same category again
        response = await async_client_auth.post(
            "/categories/", json={"name": "Entertainment", "monthly_budget": 150.0}
        )
        assert response.status_code == 400, response.json()
        assert response.json()["detail"] == "Category already exists"

    async def test_invalid_category(self, async_client_auth: AsyncClient):
        # Try creating a category with invalid data (missing monthly_budget)
        response = await async_client_auth.post(
            "/categories/", json={"name": "InvalidCategory"}
        )
        assert response.status_code == 422, response.json()


@pytest.mark.anyio
class TestCategoryCases:
    async def test_empty_category_name(self, async_client_auth: AsyncClient):
        # Test creating a category with an empty name
        response = await async_client_auth.post(
            "/categories/", json={"name": "", "monthly_budget": 100.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_zero_budget_category(self, async_client_auth: AsyncClient):
        # Test creating a category with a zero budget
        response = await async_client_auth.post(
            "/categories/", json={"name": "ZeroBudget", "monthly_budget": 0.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"

    async def test_fetch_empty_category_list(self, async_client_auth: AsyncClient):
        # Fetch all categories
        response = await async_client_auth.get("/categories/")
        assert response.status_code == 200, response.json()
        assert isinstance(response.json()["categories"], dict)

    async def test_delete_category_with_empty_name(
        self, async_client_auth: AsyncClient
    ):
        # Try deleting a category with an empty name
        response = await async_client_auth.delete("/categories/")
        assert response.status_code == 405, response.json()

    async def test_get_category_with_unusual_characters(
        self, async_client_auth: AsyncClient
    ):
        # Fetch a category with unusual characters in the name
        response = await async_client_auth.get("/categories/!@#$%^&*()")
        assert response.status_code == 404, response.json()

    async def test_create_category_with_long_name(self, async_client_auth: AsyncClient):
        # Try creating a category with an exceptionally long name
        response = await async_client_auth.post(
            "/categories/", json={"name": "Entertainment" * 50, "monthly_budget": 100.0}
        )
        assert response.status_code == 200, response.json()

    async def test_create_category_with_special_characters(
        self, async_client_auth: AsyncClient
    ):
        # Try creating a category with special characters in the name
        response = await async_client_auth.post(
            "/categories/", json={"name": "!@#%Entertainment", "monthly_budget": 100.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category created successfully"


@pytest.mark.anyio
class TestCategoryUpdate:
    async def test_update_category(self, async_client_auth: AsyncClient):
        # Update the budget of an existing category
        response = await async_client_auth.put(
            "/categories/Entertainment", json={"monthly_budget": 200.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category updated successfully"

    async def test_update_non_existent_category(self, async_client_auth: AsyncClient):
        # Try updating a non-existent category
        response = await async_client_auth.put(
            "/categories/NonExistentCategory", json={"monthly_budget": 300.0}
        )
        assert response.status_code == 404, response.json()
        assert response.json()["detail"] == "Category not found"

    async def test_update_category_with_no_changes(
        self, async_client_auth: AsyncClient
    ):
        # Update an existing category with the same data to ensure no errors
        response = await async_client_auth.put(
            "/categories/Entertainment", json={"monthly_budget": 150.0}
        )
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category updated successfully"

    async def test_update_category_negative_budget(
        self, async_client_auth: AsyncClient
    ):
        # Attempt to update a category with a negative budget
        response = await async_client_auth.put(
            "/categories/Entertainment", json={"monthly_budget": -50.0}
        )
        assert response.status_code == 400, response.json()
        assert response.json()["detail"] == "Monthly budget must be positive"


@pytest.mark.anyio
class TestGetCategories:
    async def test_get_all_categories(self, async_client_auth: AsyncClient):
        # Fetch all categories
        response = await async_client_auth.get("/categories/")
        assert response.status_code == 200, response.json()
        assert isinstance(response.json()["categories"], dict)

    async def test_get_particular_category(self, async_client_auth: AsyncClient):
        # Fetch a specific category by name
        response = await async_client_auth.get("/categories/Entertainment")
        assert response.status_code == 200, response.json()
        assert response.json()["category"]["monthly_budget"] == 150.0

    async def test_get_non_existent_category(self, async_client_auth: AsyncClient):
        # Try fetching a non-existent category
        response = await async_client_auth.get("/categories/NonExistentCategory")
        assert response.status_code == 404, response.json()

    async def test_fetch_category_case_insensitive(
        self, async_client_auth: AsyncClient
    ):
        # Fetch a category using a different case to ensure case insensitivity
        response = await async_client_auth.get("/categories/entertainment")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    async def test_fetch_large_number_of_categories(
        self, async_client_auth: AsyncClient
    ):
        # Fetch all categories to test performance with a large list
        response = await async_client_auth.get("/categories/")
        assert response.status_code == 200, response.json()
        assert isinstance(response.json()["categories"], dict)
        assert len(response.json()["categories"]) >= 10


@pytest.mark.anyio
class TestCategoryDeletion:
    async def test_delete_category(self, async_client_auth: AsyncClient):
        # Delete an existing category
        response = await async_client_auth.delete("/categories/Entertainment")
        assert response.status_code == 200, response.json()
        assert response.json()["message"] == "Category deleted successfully"

    async def test_delete_non_existent_category(self, async_client_auth: AsyncClient):
        # Try deleting a non-existent category
        response = await async_client_auth.delete("/categories/NonExistentCategory")
        assert response.status_code == 404, response.json()

    async def test_delete_category_case_insensitive(
        self, async_client_auth: AsyncClient
    ):
        # Delete a category using a different case to ensure case insensitivity
        response = await async_client_auth.delete("/categories/ENTERTAINMENT")
        assert response.status_code == 404, response.json()


@pytest.mark.anyio
class TestAdditionalCategoryCases:
    async def test_create_multiple_categories_same_budget(
        self, async_client_auth: AsyncClient
    ):
        # Create multiple categories with the same budget value to ensure no conflicts
        categories = ["Food 1", "Transport 1", "Groceries 1"]
        for cat in categories:
            response = await async_client_auth.post(
                "/categories/", json={"name": cat, "monthly_budget": 100.0}
            )
            assert response.status_code == 200, response.json()
            assert response.json()["message"] == "Category created successfully"

    async def test_create_category_invalid_budget_type(
        self, async_client_auth: AsyncClient
    ):
        # Attempt to create a category with a non-numeric budget
        response = await async_client_auth.post(
            "/categories/",
            json={"name": "NonNumericBudget", "monthly_budget": "one hundred"},
        )
        assert response.status_code == 422, response.json()

    async def test_get_category_with_unusual_characters(
        self, async_client_auth: AsyncClient
    ):
        # Fetch a category with unusual characters in the name
        response = await async_client_auth.get("/categories/!(*@(@!()))")
        assert response.status_code == 404, response.json()

    async def test_get_non_existent_category_spl_char_spaces(
        self, async_client_auth: AsyncClient
    ):
        # Try fetching a non-existent category
        response = await async_client_auth.get("/categories/!(*@ (@!()))")
        assert response.status_code == 404, response.json()
