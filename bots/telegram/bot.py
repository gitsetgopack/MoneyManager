"""POC: TELEGRAM bot"""

# pylint: skip-file

import datetime
import os

import pandas as pd
import requests
from bson import ObjectId
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import MONGO_URI, TELEGRAM_BOT_API_BASE_URL, TELEGRAM_BOT_TOKEN

# Constants
API_BASE_URL = TELEGRAM_BOT_API_BASE_URL
TSK = "None"
TOKEN_ALGORITHM = "HS256"

client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts
expenses_collection = db.expenses
telegram_collection = db.Telegram
user_tokens = {}

# Global dictionaries to track login and signup states and temporarily store usernames and passwords
LOGIN_STATE = {}
SIGNUP_STATE = {}
USERNAMES = {}
PASSWORDS = {}


##########################################################
# AUTHENTICATION
##########################################################


def authenticate(func):
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        # print("Checking auth")
        user_id = update.message.chat_id
        # print(user_id)
        user = await telegram_collection.find_one({"telegram_id": user_id})
        # print(user)
        if user and user.get("token"):
            return await func(update, context, *args, **kwargs, token=user.get("token"))
        else:
            await update.message.reply_text("You are not authenticated. Please /login")

    return wrapper


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command, providing a welcome message and instructions to log in.
    """
    if update.message:
        await update.message.reply_text(
            "Welcome to Money Manager! Please signup using /signup or log in using /login"
        )


async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiate the signup process, prompting for the username first.
    """
    user_id = update.message.chat_id if update.message else None
    SIGNUP_STATE[user_id] = "awaiting_username"
    await update.message.reply_text("To sign up, please enter your desired username:")


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiate the login process, prompting for the username first.
    """
    user_id = update.message.chat_id if update.message else None
    LOGIN_STATE[user_id] = "awaiting_username"
    await update.message.reply_text("Please enter your username:")


async def attempt_signup(update: Update, username: str, password: str):
    """
    Attempt to sign the user up with the provided username and password.
    """
    response = requests.post(
        f"{API_BASE_URL}/users/", json={"username": username, "password": password}
    )

    if response.status_code == 200:
        print("SIGNUP", username, password)
        user_id = update.message.chat_id if update.message else None
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password},
        )
        token = tokenization.json()["result"]["token"]

        user_data = {
            "username": username,
            "token": token,
            "telegram_id": user_id,
        }

        existing_user = await telegram_collection.find_one({"telegram_id": user_id})
        if existing_user:
            await telegram_collection.update_one(
                {"telegram_id": user_id}, {"$set": user_data}
            )
        else:
            await telegram_collection.insert_one(user_data)

        await update.message.reply_text(
            "Signup successful! You can now log in using /login."
        )
        return
    await update.message.reply_text(
        f"An error occurred: {response.json().get('detail', 'Unknown error')}\nPlease try again by /singup or /login"
    )


async def attempt_login(update: Update, username: str, password: str):
    """
    Attempt to log the user in with the provided username and password.
    """
    response = requests.post(
        f"{API_BASE_URL}/users/token/?token_expires=43200",
        data={"username": username, "password": password},
    )
    print("LOGGING IN")
    print(response.json())
    if response.status_code == 200:
        token = response.json()["result"]["token"]
        user_id = update.message.chat_id if update.message else None

        user = await telegram_collection.find_one({"username": username})
        if user:
            await telegram_collection.update_one(
                {"telegram_id": user_id},
                {"$set": {"token": token, "username": username}},
            )
        else:
            user_data = {
                "username": username,
                "token": token,
                "telegram_id": user_id,
            }
            await telegram_collection.insert_one(user_data)

        await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text(
            f"Login failed: {response.json()['detail']}\n /signup if you haven't, otherwise /login"
        )


##########################################################
# CATEGORIES
##########################################################


@authenticate
async def categories_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Show buttons for category actions (View, Add, Edit, Delete).
    """

    keyboard = [
        [InlineKeyboardButton("View Categories", callback_data="view_category")],
        [InlineKeyboardButton("Add Category", callback_data="add_category")],
        [InlineKeyboardButton("Edit Category", callback_data="edit_category")],
        [InlineKeyboardButton("Delete Category", callback_data="delete_category")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose an action for categories:", reply_markup=reply_markup
    )


@authenticate
async def view_category_handler(query, context, **kwargs):
    """
    Handle viewing categories with table format.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)

    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Prepare table header and rows with fixed-width formatting
        header = f"{'Category':<20} {'Monthly Budget':>15}\n"
        separator = "-" * 35
        rows = [
            f"{category:<20} {details['monthly_budget']:>15.2f}"
            for category, details in categories_data.items()
        ]

        # Combine header, separator, and rows into one string
        table_str = (
            f"Here are your available categories with budgets:\n\n\n```{header}{separator}\n"
            + "\n".join(rows)
            + "\n```"
        )

        # Send the formatted table as a message with monospaced font
        await query.edit_message_text(table_str, parse_mode="MarkdownV2")
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")


async def add_category_handler(query, context):
    """
    Handle adding a new category.
    """
    await query.edit_message_text("Please enter the name of the new category:")
    context.user_data["category_action"] = "add"
    context.user_data["category_step"] = "add_name"


@authenticate
async def edit_category_handler(query, context, **kwargs):
    """
    Display the user's categories as inline buttons to select for editing.
    """

    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)

    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Create buttons for each category
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f"edit_{category}")]
            for category in categories_data.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a category to edit:", reply_markup=reply_markup
        )
        context.user_data["category_action"] = "edit"
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")


async def handle_edit_category_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle the selection of a category for editing and prompt for a new budget.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    selected_category = query.data.replace("edit_", "")

    # Store the selected category and set up for the next step to enter a new budget
    context.user_data["selected_category"] = selected_category
    context.user_data["category_action"] = "edit"
    context.user_data["category_step"] = "edit_budget"  # Set the next expected step

    # Prompt the user to enter the new budget
    await query.edit_message_text(
        f"Enter the new monthly budget for {selected_category}:"
    )


@authenticate
async def delete_category_handler(query, context, **kwargs):
    """
    Display the user's categories as inline buttons for deletion.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)

    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Create buttons for each category
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f"delete_{category}")]
            for category in categories_data.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a category to delete:", reply_markup=reply_markup
        )
        context.user_data["category_action"] = "delete"
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")


@authenticate
async def handle_delete_category_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Handle the selection of a category for deletion and confirm deletion.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    selected_category = query.data.replace("delete_", "")

    # Confirm deletion with the user
    headers = {"token": kwargs.get("token", None)}
    response = requests.delete(
        f"{API_BASE_URL}/categories/{selected_category}", headers=headers
    )

    if response.status_code == 200:
        await query.edit_message_text(
            f"The category '{selected_category}' has been successfully deleted."
        )
    else:
        error_message = response.json().get("detail", "Failed to delete category.")
        await query.edit_message_text(f"Error: {error_message}")


@authenticate
async def delete_selected_category(query, context, selected_category, **kwargs):
    """
    Delete the specified category and notify the user of the result.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.delete(
        f"{API_BASE_URL}/categories/{selected_category}", headers=headers
    )

    # Handle the response
    if response.status_code == 200:
        await query.edit_message_text(
            f"The category '{selected_category}' has been successfully deleted."
        )
    else:
        error_message = response.json().get("detail", "Failed to delete category.")
        await query.edit_message_text(f"Error: {error_message}")


@authenticate
async def finalize_category_addition(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Finalize adding a new category by making an API request and confirm to the user.
    """
    new_category_name = context.user_data.get("new_category_name")
    new_category_budget = context.user_data.get("new_category_budget")

    # Prepare headers and payload for the API request
    headers = {
        "accept": "application/json",
        "token": kwargs.get("token", None),
        "Content-Type": "application/json",
    }
    payload = {"name": new_category_name, "monthly_budget": new_category_budget}

    # Log request details for debugging
    print("Sending request to add category")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    print(
        f"API Endpoint: https://frightening-orb-747j6q4gjjqcwr7j-9999.app.github.dev/categories/"
    )

    try:
        # Send the request to add the category
        response = requests.post(
            f"{API_BASE_URL}/categories/", json=payload, headers=headers
        )

        # Log response details
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            await update.message.reply_text(
                f"New category added successfully!\n\nCategory: {new_category_name}\nMonthly Budget: {new_category_budget}"
            )
        else:
            error_message = response.json().get(
                "detail", "An error occurred while adding the category."
            )
            await update.message.reply_text(
                f"Failed to add category. Error: {error_message}"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        await update.message.reply_text(
            "An unexpected error occurred while trying to add the category."
        )

    # Clear category addition state
    context.user_data.pop("category_action", None)
    context.user_data.pop("category_step", None)
    context.user_data.pop("new_category_name", None)
    context.user_data.pop("new_category_budget", None)


##########################################################
# EXPENSES
##########################################################


@authenticate
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Check if the user is authenticated, then handle adding an expense.
    If the user is not logged in, prompt them to log in first.
    """
    user_id = update.message.chat_id if update.message else None
    if user_id not in user_tokens:
        await update.message.reply_text(
            "Please log in using /login command before adding expenses."
        )
        return

    # Token for the authenticated user
    headers = {"token": kwargs.get("token", None)}
    response = requests.post(
        f"{API_BASE_URL}/expenses/",
        json={"amount": 100, "currency": "USD", "category": "Food"},
        headers=headers,
    )

    if response.status_code == 200:
        await update.message.reply_text("Expense added successfully!")
    else:
        error_message = response.json().get("detail", "Unknown error")
        await update.message.reply_text(
            f"Failed to add expense. Error: {error_message}"
        )


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder function for viewing balance or account details.
    """
    await update.message.reply_text("Hello, Your balance is")


async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton("View Expenses", callback_data="view_expenses")],
        [InlineKeyboardButton("Update Expense", callback_data="update_expense")],
        [InlineKeyboardButton("Delete Expense", callback_data="delete_expense")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose an expense action:", reply_markup=reply_markup
    )


@authenticate
async def add_expense_handler(query, context, **kwargs):
    """
    Start the process of adding a new expense by prompting for the amount.
    """
    await query.edit_message_text("Please enter the amount:")
    context.user_data["expense_action"] = "add"
    context.user_data["expense_step"] = "amount"


@authenticate
async def view_expenses_handler(query, context, **kwargs):
    """
    Handle viewing expenses and display them in a formatted list.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/expenses/", headers=headers)

    if response.status_code == 200:
        expenses_data = response.json().get("expenses", [])
        expense_list = "\n".join(
            [
                f"{i+1}. {exp['category']} - {exp['amount']} {exp['currency']} on {exp['date']}"
                for i, exp in enumerate(expenses_data)
            ]
        )
        await query.edit_message_text(f"Your recent expenses:\n\n{expense_list}")
    else:
        await query.edit_message_text("Unable to retrieve expenses.")


@authenticate
async def update_expense_handler(query, context, **kwargs):
    """
    Start the process to update an expense by selecting one from the list.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/expenses/", headers=headers)

    if response.status_code == 200:
        expenses_data = response.json().get("expenses", [])

        # Display each expense as a button to select for updating
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{exp['category']} - {exp['amount']} {exp['currency']}",
                    callback_data=f"update_{exp['_id']}",
                )
            ]
            for exp in expenses_data
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select an expense to update:", reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Error fetching expenses for update.")


@authenticate
async def delete_expense_handler(query, context, **kwargs):
    """
    Handle selecting and deleting an expense.
    """
    headers = {"token": kwargs.get("token", None)}
    response = requests.get(f"{API_BASE_URL}/expenses/", headers=headers)

    if response.status_code == 200:
        expenses_data = response.json().get("expenses", [])

        # Display each expense as a button to select for deletion
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{exp['category']} - {exp['amount']} {exp['currency']}",
                    callback_data=f"delete_{exp['_id']}",
                )
            ]
            for exp in expenses_data
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select an expense to delete:", reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("Error fetching expenses for deletion.")


async def handle_expense_update_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle selection of an expense for updating and prompt for new amount.
    """
    query = update.callback_query
    await query.answer()
    expense_id = query.data.replace("update_", "")
    context.user_data["expense_id"] = expense_id
    context.user_data["expense_action"] = "update"
    context.user_data["expense_step"] = "new_amount"

    await query.edit_message_text("Please enter the new amount for this expense:")


async def handle_expense_delete_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle the confirmation and deletion of a selected expense.
    """
    query = update.callback_query
    await query.answer()
    expense_id = query.data.replace("delete_", "")
    headers = {"token": context.user_data.get("token", None)}

    response = requests.delete(f"{API_BASE_URL}/expenses/{expense_id}", headers=headers)

    if response.status_code == 200:
        await query.edit_message_text("Expense deleted successfully!")
    else:
        await query.edit_message_text("Failed to delete expense.")


@authenticate
async def finalize_expense_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Finalize updating an expense by applying the new amount and category.
    """
    expense_id = context.user_data.get("expense_id")
    new_amount = context.user_data.get("new_amount")
    headers = {"token": kwargs.get("token", None)}
    payload = {"amount": new_amount}

    response = requests.put(
        f"{API_BASE_URL}/expenses/{expense_id}", json=payload, headers=headers
    )

    if response.status_code == 200:
        await update.message.reply_text("Expense updated successfully!")
    else:
        await update.message.reply_text("Failed to update expense.")

    context.user_data.pop("expense_action", None)
    context.user_data.pop("expense_step", None)
    context.user_data.pop("expense_id", None)
    context.user_data.pop("new_amount", None)


@authenticate
async def finalize_expense(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Finalize the expense entry by sending it to the API and notifying the user of success.
    """
    amount = context.user_data.get("amount")
    category = context.user_data.get("category")
    date = context.user_data.get("date")

    headers = {"token": kwargs.get("token", None)}
    payload = {
        "amount": amount,
        "category": category,
        "currency": "USD",
        "date": date.strftime("%Y-%m-%d"),
    }

    response = requests.post(f"{API_BASE_URL}/expenses/", json=payload, headers=headers)

    if response.status_code == 200:
        await update.message.reply_text(
            f"Expense added successfully!\n\nAmount: {amount}\nCategory: {category}\nDate: {date}"
        )
    else:
        error_message = response.json().get(
            "detail", "An error occurred while adding the expense."
        )
        await update.message.reply_text(
            f"Failed to add expense. Error: {error_message}"
        )

    # Clear context data related to the expense entry
    context.user_data.pop("expense_action", None)
    context.user_data.pop("expense_step", None)
    context.user_data.pop("amount", None)
    context.user_data.pop("category", None)
    context.user_data.pop("date", None)


# Unified callback query handler to handle each expense action based on callback data
@authenticate
async def unified_expense_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("update_"):
        await handle_expense_update_selection(update, context)
    elif query.data.startswith("delete_"):
        await handle_expense_delete_selection(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages and direct messages to appropriate handlers based on context.
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""

    # Check if user is in the signup process
    if user_id in SIGNUP_STATE:
        if SIGNUP_STATE[user_id] == "awaiting_username":
            # Store the username and prompt for password
            USERNAMES[user_id] = text
            SIGNUP_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your desired password:")

        elif SIGNUP_STATE[user_id] == "awaiting_password":
            # Retrieve username and password, then attempt signup
            username = USERNAMES.get(user_id)
            password = text
            await attempt_signup(update, username, password)
            # Clear signup state after attempting signup
            SIGNUP_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Check if user is in login process
    if user_id in LOGIN_STATE:
        if LOGIN_STATE[user_id] == "awaiting_username":
            # Store the username and prompt for password
            USERNAMES[user_id] = text
            LOGIN_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your password:")

        elif LOGIN_STATE[user_id] == "awaiting_password":
            # Retrieve username and password, then attempt login
            username = USERNAMES.get(user_id)
            password = text
            await attempt_login(update, username, password)
            # Clear login state after attempting login
            LOGIN_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

        await handle_response(update, text)


async def fallback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unrecognized command")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline button actions for expenses.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == "add_expense":
        await add_expense_handler(query, context)
    elif query.data == "delete_expense":
        await delete_expense_handler(query, context)
    elif query.data == "view_expenses":
        await view_expenses_handler(query, context)


@authenticate
async def combined_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs
):
    """
    Combined handler for handling category and expense inputs step-by-step.
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""

    # Check if the user is in the process of adding an expense
    if context.user_data.get("expense_action") == "add":
        # Process expense input step by step
        if context.user_data.get("expense_step") == "amount":
            try:
                amount = float(text)
                context.user_data["amount"] = amount
                context.user_data["expense_step"] = "category"
                await update.message.reply_text(
                    "Please enter the category (e.g., Food):"
                )
            except ValueError:
                await update.message.reply_text(
                    "Invalid amount. Please enter a numeric value."
                )
            return

        elif context.user_data.get("expense_step") == "category":
            context.user_data["category"] = text
            context.user_data["expense_step"] = "date"
            await update.message.reply_text("Please enter the date (YYYY-MM-DD):")
            return

        elif context.user_data.get("expense_step") == "date":
            try:
                date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
                context.user_data["date"] = date
                await finalize_expense(update, context)
            except ValueError:
                await update.message.reply_text(
                    "Invalid date format. Please enter a date in YYYY-MM-DD format."
                )
            return

    # Check if the user is in the process of updating an expense
    elif context.user_data.get("expense_action") == "update":
        if context.user_data.get("expense_step") == "new_amount":
            try:
                new_amount = float(text)
                context.user_data["new_amount"] = new_amount
                await finalize_expense_update(update, context)
            except ValueError:
                await update.message.reply_text(
                    "Invalid amount. Please enter a numeric value."
                )
            return

    # Check if the user is in the process of adding a new category
    elif context.user_data.get("category_action") == "add":
        if context.user_data.get("category_step") == "add_name":
            context.user_data["new_category_name"] = text
            context.user_data["category_step"] = "add_budget"
            await update.message.reply_text(
                "Please enter the monthly budget for this category:"
            )
            return

        elif context.user_data.get("category_step") == "add_budget":
            try:
                monthly_budget = float(text)
                context.user_data["new_category_budget"] = monthly_budget
                await finalize_category_addition(update, context)
            except ValueError:
                await update.message.reply_text(
                    "Invalid budget. Please enter a numeric value."
                )
            return

    # Check if the user is in the process of editing a category's budget
    elif context.user_data.get("category_action") == "edit":
        if context.user_data.get("category_step") == "edit_budget":
            try:
                new_budget = float(text)
                selected_category = context.user_data.get("selected_category")

                # Update the category budget in the database
                headers = {"token": kwargs.get("token", None)}
                payload = {"name": selected_category, "monthly_budget": new_budget}
                response = requests.put(
                    f"{API_BASE_URL}/categories/{selected_category}",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    await update.message.reply_text(
                        f"The budget for {selected_category} has been updated to {new_budget}."
                    )
                else:
                    error_message = response.json().get(
                        "detail", "Failed to update category."
                    )
                    await update.message.reply_text(f"Error: {error_message}")

            except ValueError:
                await update.message.reply_text(
                    "Invalid budget. Please enter a numeric value."
                )

            # Clear context data after updating
            context.user_data.pop("category_action", None)
            context.user_data.pop("category_step", None)
            context.user_data.pop("selected_category", None)
            return

    # Check if the user is in the signup process
    elif user_id in SIGNUP_STATE:
        if SIGNUP_STATE[user_id] == "awaiting_username":
            USERNAMES[user_id] = text
            SIGNUP_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your desired password:")
        elif SIGNUP_STATE[user_id] == "awaiting_password":
            username = USERNAMES.get(user_id)
            password = text
            await attempt_signup(update, username, password)
            SIGNUP_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Check if the user is in the login process
    elif user_id in LOGIN_STATE:
        if LOGIN_STATE[user_id] == "awaiting_username":
            USERNAMES[user_id] = text
            LOGIN_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your password:")
        elif LOGIN_STATE[user_id] == "awaiting_password":
            username = USERNAMES.get(user_id)
            password = text
            await attempt_login(update, username, password)
            LOGIN_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Handle general messages or unrecognized commands
    else:
        await handle_general_message(update, context)


async def unified_callback_query_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Unified handler for all callback queries related to categories and expenses.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Debugging print to check if the handler is triggered
    print("CallbackQueryHandler triggered with data:", query.data)

    data = query.data  # The callback data from the button clicked

    # Handle the different callback actions
    if data == "edit_category":
        await edit_category_handler(query, context)
    elif data == "delete_category":
        await delete_category_handler(query, context)
    elif data.startswith("edit_"):
        selected_category = data.replace("edit_", "")
        context.user_data["selected_category"] = selected_category
        context.user_data["category_action"] = "edit"
        context.user_data["category_step"] = "edit_budget"
        await query.edit_message_text(
            f"Enter the new monthly budget for {selected_category}:"
        )
    elif data.startswith("delete_"):

        selected_category = data.replace("delete_", "")
        await delete_selected_category(query, context, selected_category)

    if query.data.startswith("update_"):
        await handle_expense_update_selection(update, context)

    elif data == "view_category":
        # Handle view categories (this can be expanded as needed)
        await view_category_handler(query, context)

    elif data == "add_category":
        # Handle add category
        await add_category_handler(query, context)

    elif data == "edit_category":
        # Show categories for editing
        await edit_category_handler(query, context)

    elif data == "delete_category":

        # Show categories for deletion
        await delete_category_handler(query, context)

    # Handle expense-related actions
    elif data == "add_expense":
        await add_expense_handler(query, context)
    elif data == "view_expenses":
        await view_expenses_handler(query, context)
    elif data == "update_expense":
        await update_expense_handler(query, context)
    elif data == "delete_expense":
        await delete_expense_handler(query, context)

    else:
        # Fallback for unrecognized data
        await query.edit_message_text("Unknown action. Please try again.")


async def handle_general_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    General message handler for other text messages.
    """
    text = update.message.text
    if text.lower() in ("hi", "hello"):
        await update.message.reply_text("Hello! How can I assist you today?")
    else:
        await update.message.reply_text(
            "Sorry, I didn't understand that. Please use /help to see available commands."
        )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Log and handle errors that occur during the bot's operation.
    """
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting Bot..")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("signup", signup_command))
    app.add_handler(CommandHandler("categories", categories_command))
    app.add_handler(CommandHandler("expenses", expense_command))
    app.add_handler(CallbackQueryHandler(unified_callback_query_handler))

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE, combined_message_handler
        )
    )
    app.add_handler(MessageHandler(filters.COMMAND, fallback_command))
    app.add_error_handler(error)
    print("Polling..")
    app.run_polling(poll_interval=3)
