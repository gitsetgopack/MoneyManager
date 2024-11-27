"""
This module provides endpoints for managing user expenses in the Money Manager application.
"""

import datetime
import io
from typing import Optional

import chardet
import pandas as pd
from bson import ObjectId
from currency_converter import CurrencyConverter  # type: ignore
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from api.utils.auth import verify_token
from config import MONGO_URI

currency_converter = CurrencyConverter()

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
expenses_collection = db.expenses
accounts_collection = db.accounts


def format_id(document):
    """Convert MongoDB document ID to string."""
    document["_id"] = str(document["_id"])
    return document


def convert_currency(amount, from_cur, to_cur):
    """Convert currency using the CurrencyConverter library."""
    if from_cur == to_cur:
        return amount
    try:
        return currency_converter.convert(amount, from_cur, to_cur)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Currency conversion failed: {str(e)}"
        ) from e


class ExpenseCreate(BaseModel):
    """Model for creating an expense."""

    amount: float
    currency: str
    category: str
    description: Optional[str] = None
    account_name: str = "Checking"
    date: Optional[datetime.datetime] = None


class ExpenseUpdate(BaseModel):
    """Model for updating an expense."""

    amount: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    # TODO: add account_name changing capability also
    date: Optional[datetime.datetime] = None


@router.post("/")
async def add_expense(expense: ExpenseCreate, token: str = Header(None)):
    """
    Add a new expense for the user.

    Args:
        expense (ExpenseCreate): Expense details.
        token (str): Authentication token.

    Returns:
        dict: Message with expense details and updated balance.
    """
    user_id = await verify_token(token)
    account = await accounts_collection.find_one(
        {"user_id": user_id, "name": expense.account_name}
    )
    if not account:
        raise HTTPException(status_code=400, detail="Invalid account type")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expense.currency = expense.currency.upper()
    if expense.currency not in user["currencies"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Currency type is not added to user account. "
                f"Available currencies are {user['currencies']}"
            ),
        )
    converted_amount = convert_currency(
        expense.amount, expense.currency, account["currency"]
    )

    if account["balance"] < converted_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance in {expense.account_name} account",
        )

    if expense.category not in user["categories"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Category is not present in the user account. "
                f"Available categories are {list(user['categories'])}"
            ),
        )

    # Deduct amount from user's account balance
    new_balance = account["balance"] - converted_amount
    await accounts_collection.update_one(
        {"_id": account["_id"]}, {"$set": {"balance": new_balance}}
    )

    # Convert date to datetime object or use current datetime if none is provided
    expense_date = expense.date or datetime.datetime.now(datetime.timezone.utc)
    # Record the expense
    expense_data = expense.dict()
    expense_data.update(
        {
            "user_id": user_id,
            "date": expense_date,
        }
    )
    result = await expenses_collection.insert_one(expense_data)

    if result.inserted_id:
        expense_data["date"] = expense_date  # Ensure consistent formatting for response
        return {
            "message": "Expense added successfully",
            "expense": format_id(expense_data),
            "balance": new_balance,
        }
    raise HTTPException(status_code=500, detail="Failed to add expense")


@router.get("/")
async def get_expenses(token: str = Header(None)):
    """
    Get all expenses for a user.

    Args:
        token (str): Authentication token.

    Returns:
        dict: List of expenses.
    """
    user_id = await verify_token(token)
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(1000)
    formatted_expenses = [format_id(expense) for expense in expenses]
    return {"expenses": formatted_expenses}


@router.get("/{expense_id}")
async def get_expense(expense_id: str, token: str = Header(None)):
    """
    Get a specific expense by ID.

    Args:
        expense_id (str): ID of the expense.
        token (str): Authentication token.

    Returns:
        dict: Details of the specified expense.
    """
    user_id = await verify_token(token)
    expense = await expenses_collection.find_one(
        {"user_id": user_id, "_id": ObjectId(expense_id)}
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return format_id(expense)


@router.delete("/all")
async def delete_all_expenses(token: str = Header(None)):
    """
    Delete all expenses for the authenticated user and update account balances.

    Args:
        token (str): Authentication token.

    Returns:
        dict: Message indicating the number of expenses deleted.
    """
    user_id = await verify_token(token)

    # Retrieve all expenses for the user before deletion
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(None)
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found to delete")

    # Organize expenses by account name to sum them for each account
    account_adjustments: dict[str, float] = {}
    for expense in expenses:
        account_name = expense.get("account_name")
        amount = expense.get("amount", 0)

        # Find the account ID by name
        account = await accounts_collection.find_one(
            {"name": account_name, "user_id": user_id}
        )
        if account:
            account_id = account["_id"]
            if account_id in account_adjustments:
                account_adjustments[account_id] += amount
            else:
                account_adjustments[account_id] = amount

    # Update each account's balance
    for account_id, total_expense_amount in account_adjustments.items():
        await accounts_collection.update_one(
            {"_id": account_id, "user_id": user_id},
            {"$inc": {"balance": total_expense_amount}},
        )

    # Delete all expenses
    result = await expenses_collection.delete_many({"user_id": user_id})

    return {"message": f"{result.deleted_count} expenses deleted successfully"}


@router.delete("/{expense_id}")
async def delete_expense(expense_id: str, token: str = Header(None)):
    """
    Delete an expense by ID.

    Args:
        expense_id (str): ID of the expense to delete.
        token (str): Authentication token.

    Returns:
        dict: Message with updated balance.
    """
    user_id = await verify_token(token)
    expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})

    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    account_name = expense["account_name"]
    account = await accounts_collection.find_one(
        {"user_id": user_id, "name": account_name}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    amount = convert_currency(
        expense["amount"], expense["currency"], account["currency"]
    )

    # Refund the amount to user's account
    new_balance = account["balance"] + amount
    await accounts_collection.update_one(
        {"_id": account["_id"]}, {"$set": {"balance": new_balance}}
    )

    # Delete the expense
    result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})

    if result.deleted_count == 1:
        return {"message": "Expense deleted successfully", "balance": new_balance}
    raise HTTPException(status_code=500, detail="Failed to delete expense")


@router.put("/{expense_id}")
# pylint: disable=too-many-locals
async def update_expense(
    expense_id: str, expense_update: ExpenseUpdate, token: str = Header(None)
):
    """
    Update an expense by ID.

    Args:
        expense_id (str): ID of the expense to update.
        expense_update (ExpenseUpdate): Expense update details.
        token (str): Authentication token.

    Returns:
        dict: Message with updated expense and balance.
    """
    user_id = await verify_token(token)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_fields: dict[str, str | float | datetime.datetime] = {}

    def validate_currency():
        if expense_update.currency:
            expense_update.currency = expense_update.currency.upper()
            if expense_update.currency not in user["currencies"]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Currency type is not added to user account. "
                        f"Available currencies are {user['currencies']}"
                    ),
                )
            update_fields["currency"] = expense_update.currency

    async def validate_amount():
        nonlocal new_balance
        if expense_update.amount is not None:
            update_fields["amount"] = expense_update.amount

            # Adjust the user's balance
            # Convert old and new amounts to the account currency to determine balance adjustment
            original_amount_converted = convert_currency(
                expense["amount"], expense["currency"], account["currency"]
            )
            new_amount_converted = convert_currency(
                expense_update.amount,
                expense_update.currency or expense["currency"],
                account["currency"],
            )

            difference = new_amount_converted - original_amount_converted
            new_balance = account["balance"] - difference

            if new_balance < 0:
                raise HTTPException(
                    status_code=400, detail="Insufficient balance to update the expense"
                )
            await accounts_collection.update_one(
                {"_id": account["_id"]}, {"$set": {"balance": new_balance}}
            )

    def validate_category():
        if expense_update.category:
            if expense_update.category not in user["categories"]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Category is not present in the user account. "
                        f"Available categories are {list(user['categories'])}"
                    ),
                )
            update_fields["category"] = expense_update.category

    def validate_description():
        if expense_update.description:
            update_fields["description"] = expense_update.description

    def validate_date():
        if expense_update.date:
            update_fields["date"] = expense_update.date

    # Run validations
    validate_currency()
    account_name = expense["account_name"]
    account = await accounts_collection.find_one(
        {"user_id": user_id, "name": account_name}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    new_balance = account["balance"]
    await validate_amount()
    validate_category()
    validate_description()
    validate_date()

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await expenses_collection.update_one(
        {"_id": ObjectId(expense_id)}, {"$set": update_fields}
    )
    if result.modified_count == 1:
        updated_expense = await expenses_collection.find_one(
            {"_id": ObjectId(expense_id)}
        )
        return {
            "message": "Expense updated successfully",
            "updated_expense": format_id(updated_expense),
            "balance": new_balance,
        }
    raise HTTPException(status_code=500, detail="Failed to update expense")


@router.get("/export/excel")
async def export_expenses_to_excel(token: str = Header(None)):
    """Export expense data to an Excel file"""
    user_id = await verify_token(token)
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(None)

    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found.")

    # Convert MongoDB documents to DataFrame
    for expense in expenses:
        expense["_id"] = str(
            expense["_id"]
        )  # Convert ObjectId to string for compatibility

    df = pd.DataFrame(expenses)

    # Drop '_id' and 'user_id' columns
    df.drop(columns=["_id", "user_id"], inplace=True, errors="ignore")

    # Move 'description' column to the first position
    if "description" in df.columns:
        description_column = df.pop(
            "description"
        )  # Remove and get 'description' column
        df.insert(
            0, "description", description_column
        )  # Insert it at the first position

    # Create an in-memory file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Expenses")
        # workbook = writer.book
        sheet = writer.sheets["Expenses"]

        # Auto-adjust column width
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter  # Get column letter
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:  # pylint: disable=W0702  # nosec B110
                    pass
            adjusted_width = max_length + 2
            sheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=expenses.xlsx"},
    )


@router.post("/import/csv")
async def import_expenses_from_csv(
    token: str = Header(None), file: UploadFile = File(...)
):
    """
    Import expenses from a CSV file.

    Args:
        token (str): Authentication token.
        file (UploadFile): The uploaded CSV file.

    Returns:
        dict: Message indicating success or failure.
    """
    user_id = await verify_token(token)

    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a CSV file."
        )

    try:
        content = await file.read()
        result = chardet.detect(content)
        encoding = result["encoding"]

        # Read the CSV file
        df = pd.read_csv(io.BytesIO(content), encoding=encoding)

        # Validate required columns
        required_columns = {
            "description",
            "amount",
            "currency",
            "category",
            "account_name",
            "date",
        }
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns. Expected: {', '.join(required_columns)}",
            )

        # Drop rows where all fields are NaN
        df = df.dropna(how="all")

        # Ensure 'date' column is properly formatted
        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        )  # Convert invalid dates to NaT

        # Drop rows with missing required fields
        required_fields = [
            "description",
            "amount",
            "currency",
            "category",
            "account_name",
            "date",
        ]
        df = df.dropna(subset=required_fields)

        # Process each row and add expenses to the database
        for _, row in df.iterrows():
            expense = {
                "description": row["description"],
                "amount": row["amount"],
                "currency": row["currency"].upper(),
                "category": row["category"],
                "account_name": row["account_name"],
                "date": row["date"],  # Already converted to datetime
                "user_id": user_id,
            }

            # Check if the account exists for the user
            account = await accounts_collection.find_one(
                {"user_id": user_id, "name": expense["account_name"]}
            )
            if not account:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid account name: {expense['account_name']}",
                )

            # Insert expense into the database
            await expenses_collection.insert_one(expense)

        return {"message": "Expenses imported successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process CSV: {str(e)}"
        ) from e
