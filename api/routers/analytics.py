"""
This module provides analytics endpoints for retrieving and visualizing
expense data. It includes routes to generate visualizations for expenses
from a specified number of days.

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

import base64
import io
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api.utils.auth import verify_token
from config import MONGO_URI

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
expenses_collection = db.expenses

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/expense/bar", response_class=HTMLResponse)
async def expense_bar(x_days: int, token: str = Header(None)):
    """
    Endpoint to generate a bar chart of daily expenses for the previous x_days.
    Args:
        x_days (int): The number of days to look back for expense data.
        token (str): Authorization token for user verification.
    Returns:
        HTMLResponse: An HTML page displaying the bar chart.
    """
    # Verify token and retrieve user_id
    user_id = await verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Define the date range filter for MongoDB query
    date_filter = {
        "date": {"$gte": datetime.now() - timedelta(days=x_days)},
        "user_id": user_id,
    }

    # Fetch expenses data from MongoDB
    expenses = await expenses_collection.find(date_filter).to_list(length=1000)

    if not expenses:
        raise HTTPException(
            status_code=404, detail="No expenses found for the specified period"
        )

    # Convert to DataFrame and process data
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    daily_expenses = df.groupby(df["date"].dt.date)["amount"].sum()

    # Plotting the bar graph
    plt.figure(figsize=(10, 6))
    ax = daily_expenses.plot(kind="bar", color="skyblue")
    plt.title(f"Total Expenses per Day (Last {x_days} Days)")
    plt.xlabel("Date")
    plt.ylabel("Total Expense Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Adding labels on top of each bar
    for i, value in enumerate(daily_expenses):
        ax.text(
            i,
            value + 0.5,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
        )

    # Convert the plot to a base64-encoded image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Return the HTML response with the embedded image
    return HTMLResponse(
        content=f"""
        <html>
            <head><title>Expense Bar Chart</title></head>
            <body>
                <h1>Total Expenses per Day (Last {x_days} Days)</h1>
                <img src="data:image/png;base64,{image_data}" alt="Expense Bar Chart">
            </body>
        </html>
        """
    )


@router.get("/expense/pie", response_class=HTMLResponse)
async def expense_pie(x_days: int, token: str = Header(None)):
    """
    Endpoint to generate a pie chart of expenses categorized by type for the previous x_days.
    Args:
        x_days (int): The number of days to look back for expense data.
        token (str): Authorization token for user verification.
    Returns:
        HTMLResponse: An HTML page displaying the pie chart.
    """
    # Verify token and retrieve user_id
    user_id = await verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Define the date range filter for MongoDB query
    date_filter = {
        "date": {"$gte": datetime.now() - timedelta(days=x_days)},
        "user_id": user_id,
    }

    # Fetch expenses data from MongoDB
    expenses = await expenses_collection.find(date_filter).to_list(length=1000)

    if not expenses:
        raise HTTPException(
            status_code=404, detail="No expenses found for the specified period"
        )

    # Convert to DataFrame and process data
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])

    # Group by category and sum the amounts
    category_expenses = df.groupby("category")["amount"].sum()

    # Plotting the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        category_expenses,
        labels=category_expenses.index.astype(str).tolist(),
        autopct="%1.1f%%",
        startangle=140,
        colors=["#FF9999", "#FF4D4D", "#FF0000"],
    )
    plt.title(f"Expense Distribution by Category (Last {x_days} Days)")
    plt.axis("equal")  # Equal aspect ratio ensures that pie chart is circular.

    # Convert the plot to a base64-encoded image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Return the HTML response with the embedded image
    return HTMLResponse(
        content=f"""
        <html>
            <head><title>Expense Pie Chart</title></head>
            <body>
                <h1>Expense Distribution by Category (Last {x_days} Days)</h1>
                <img src="data:image/png;base64,{image_data}" alt="Expense Pie Chart">
            </body>
        </html>
        """
    )
