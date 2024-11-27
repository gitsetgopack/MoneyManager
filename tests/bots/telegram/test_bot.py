import time
from unittest.mock import AsyncMock, patch

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from bots.telegram.bot import (
    categories_command,
    expense_command,
    handle_message,
    login_command,
    signup_command,
    start_command,
    unified_callback_query_handler,
)

# # Fixture to mock Update and Context for testing
# @pytest.fixture
# def mock_update():
#     mock_update = AsyncMock(spec=Update)
#     mock_update.message = AsyncMock()
#     mock_update.callback_query = AsyncMock()
#     mock_update.message.chat_id = 12345
#     return mock_update


# @pytest.fixture
# def mock_context():
#     return AsyncMock(spec=CallbackContext)


# # Test start command
# @pytest.mark.asyncio
# async def test_start_command(mock_update, mock_context):
#     await start_command(mock_update, mock_context)
#     mock_update.message.reply_text.assert_called_once_with(
#         "Welcome to Money Manager! Please signup using /signup or log in using /login"
#     )


# # Test login command
# @pytest.mark.asyncio
# async def test_login_command(mock_update, mock_context):
#     await login_command(mock_update, mock_context)
#     mock_update.message.reply_text.assert_called_once_with(
#         "Please enter your username:"
#     )


# # Test signup command
# @pytest.mark.asyncio
# async def test_signup_command(mock_update, mock_context):
#     await signup_command(mock_update, mock_context)
#     mock_update.message.reply_text.assert_called_once_with(
#         "To sign up, please enter your desired username:"
#     )


# # Test expense command with buttons
# @pytest.mark.asyncio
# async def test_expense_command(mock_update, mock_context):
#     await expense_command(mock_update, mock_context)
#     buttons = [
#         [InlineKeyboardButton("Add Expense", callback_data="add_expense")],
#         [InlineKeyboardButton("View Expenses", callback_data="view_expenses")],
#         [InlineKeyboardButton("Update Expense", callback_data="update_expense")],
#         [InlineKeyboardButton("Delete Expense", callback_data="delete_expense")],
#     ]
#     expected_markup = InlineKeyboardMarkup(buttons)
#     mock_update.message.reply_text.assert_called_once_with(
#         "Choose an expense action:", reply_markup=expected_markup
#     )


# # Test unified callback query handler for each callback data case
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "callback_data, handler_patch",
#     [
#         ("view_category", "view_category_handler"),
#         ("add_category", "add_category_handler"),
#         ("add_expense", "add_expense_handler"),
#         ("view_expenses", "view_expenses_handler"),
#     ],
# )
# async def test_unified_callback_handlers(
#     callback_data, handler_patch, mock_update, mock_context
# ):
#     mock_update.callback_query.data = callback_data
#     with patch(f"bots.telegram.bot.{handler_patch}") as mock_handler:
#         await unified_callback_query_handler(mock_update, mock_context)
#         mock_handler.assert_called_once_with(mock_update.callback_query, mock_context)
#     time.sleep(3)
