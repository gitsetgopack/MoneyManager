"""
This module defines the main FastAPI application for Money Manager.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routers import accounts, analytics, categories, expenses, users
from config import API_BIND_HOST, API_BIND_PORT


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan function that handles app startup and shutdown"""
    yield
    # Handles the shutdown event to close the MongoDB client
    await users.shutdown_db_client()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="api/static"), name="static")
app.mount("/logo", StaticFiles(directory="docs/logo"), name="logo")
app.mount("/backgrounds", StaticFiles(directory="docs/backgrounds"), name="backgrounds")

# templates
templates = Jinja2Templates(directory="api/templates")

# routers for different functionalities
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(analytics.router)


# default web app route
@app.get("/")
async def read_root():
    """Default pathway"""
    return RedirectResponse(url="/login", status_code=302)


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    """Calls the logout functionality"""
    result = await users.logout(response, request)

    if result.get("message") == "Logout successful":
        redirect_response = RedirectResponse(url="/login", status_code=302)
        if "set-cookie" in response.headers:
            redirect_response.headers["set-cookie"] = response.headers[
                "set-cookie"
            ]  # the fix to the cookie not invalidating after 2 hours of debugging
        return redirect_response

    raise HTTPException(status_code=400, detail="Logout failed")


@app.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request, token: Optional[str] = Header(None)):
    """Load the landing/home page"""
    token = request.cookies.get("access_token")  # retrieve token from cookies
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        username = await users.get_username(token)
        return templates.TemplateResponse(
            "accounts.html", {"request": request, "username": username}
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@app.get("/categories", response_class=HTMLResponse)
async def category(request: Request, token: Optional[str] = Header(None)):
    """gets categories"""
    token = request.cookies.get("access_token")  # retrieve token from cookies
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        username = await users.get_username(token)
        return templates.TemplateResponse(
            "categories.html", {"request": request, "username": username}
        )
    except HTTPException:
        return RedirectResponse(url="/landing", status_code=302)


@app.get("/expenses", response_class=HTMLResponse)
async def expense(request: Request, token: Optional[str] = Header(None)):
    """gets current expenses"""
    token = request.cookies.get("access_token")  # retrieve token from cookies
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        username = await users.get_username(token)
        return templates.TemplateResponse(
            "expenses.html", {"request": request, "username": username}
        )
    except HTTPException:
        return RedirectResponse(url="/landing", status_code=302)


@app.get("/barchart", response_class=HTMLResponse)
async def barchart(request: Request, token: Optional[str] = Header(None)):
    """loads the bar chart"""
    token = request.cookies.get("access_token")  # retrieve token from cookies
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        username = await users.get_username(token)
        return templates.TemplateResponse(
            "barchart.html", {"request": request, "username": username}
        )
    except HTTPException:
        return RedirectResponse(url="/landing", status_code=302)


@app.get("/piechart", response_class=HTMLResponse)
async def piechart(request: Request, token: Optional[str] = Header(None)):
    """loads the pie chart"""
    token = request.cookies.get("access_token")  # retrieve token from cookies
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        username = await users.get_username(token)
        return templates.TemplateResponse(
            "piechart.html", {"request": request, "username": username}
        )
    except HTTPException:
        return RedirectResponse(url="/landing", status_code=302)


@app.get("/docs/logo/MoneyManagerLOGO.png")
async def get_image():
    """loads the site logo"""
    image_path = Path("/docs/logo/MoneyManagerLOGO.png")
    if not image_path.is_file():
        return {"error": "image not found"}
    return FileResponse(image_path)


if __name__ == "__main__":
    uvicorn.run("app:app", host=API_BIND_HOST, port=API_BIND_PORT, reload=True)
