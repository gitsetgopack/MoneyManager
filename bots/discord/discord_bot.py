# pylint: skip-file

import discord
import requests
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

from config import DISCORD_TOKEN, MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
discord_collection = db.Discord

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# The public URL from Pinggy
API_BASE_URL = "https://rnvcj-172-58-251-251.a.free.pinggy.link"  # Replace with your actual Pinggy URL

LOGIN_STATE = {}
SIGNUP_STATE = {}


@bot.event
async def on_ready():
    """Triggered when the bot is ready and connected to Discord."""
    print(f"Logged in as {bot.user}")


@bot.command()
async def expose(ctx):
    """Command to expose the FastAPI app using Pinggy.io"""
    print("Expose command triggered!")
    await ctx.send(f"Your web app is now exposed at: {API_BASE_URL}")


@bot.command()
async def start(ctx):
    """Handle the start command"""
    await ctx.send(
        "Welcome to Money Manager! Use !signup to create an account or !login to log in."
    )


@bot.command()
async def signup(ctx):
    """Handle the signup command"""
    user_id = ctx.author.id
    SIGNUP_STATE[user_id] = "awaiting_username"
    await ctx.send("To sign up, please enter your desired username:")


@bot.command()
async def login(ctx):
    """Handle the login command"""
    user_id = ctx.author.id
    LOGIN_STATE[user_id] = "awaiting_username"
    await ctx.send("Please enter your username:")


@bot.command()
async def cancel(ctx):
    """Cancel any ongoing signup or login process"""
    user_id = ctx.author.id
    if user_id in SIGNUP_STATE:
        del SIGNUP_STATE[user_id]
        await ctx.send("Signup process cancelled.")
    elif user_id in LOGIN_STATE:
        del LOGIN_STATE[user_id]
        await ctx.send("Login process cancelled.")
    else:
        await ctx.send("There is no ongoing process to cancel.")


# Handle messages from users for signup process
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id

    # If the user is in the signup process and awaiting a username
    if user_id in SIGNUP_STATE and SIGNUP_STATE[user_id] == "awaiting_username":
        username = message.content.strip()
        SIGNUP_STATE[user_id] = "awaiting_password"  # Next step: password input
        await message.channel.send(
            f"Username {username} received! Now, please enter your password:"
        )

        # Store the username in a temporary dictionary (or database) for the next step
        SIGNUP_STATE[user_id] = {"username": username, "step": "awaiting_password"}
        return

    # If the user is in the signup process and awaiting a password
    if (
        user_id in SIGNUP_STATE
        and SIGNUP_STATE[user_id].get("step") == "awaiting_password"
    ):
        password = message.content.strip()
        username = SIGNUP_STATE[user_id]["username"]  # Retrieve username from earlier

        # Proceed with signup attempt
        await attempt_signup(message, username, password)

        # Cleanup the signup state
        del SIGNUP_STATE[user_id]
        return

    # Let commands still work normally (if no signup process is active)
    await bot.process_commands(message)


async def attempt_signup(message, username: str, password: str):
    """Attempt to sign the user up with the provided username and password."""
    user_id = message.author.id  # Using message.author.id to get the user ID
    response = requests.post(
        f"{API_BASE_URL}/users/", json={"username": username, "password": password}
    )
    if response.status_code == 200:
        # Generate token after signup
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password},
        )
        token = tokenization.json()["result"]["token"]

        user_data = {
            "username": username,
            "token": token,
            "discord_id": user_id,
        }

        existing_user = await discord_collection.find_one({"discord_id": user_id})
        if existing_user:
            await discord_collection.update_one(
                {"discord_id": user_id}, {"$set": user_data}
            )
        else:
            await discord_collection.insert_one(user_data)

        # Send the message to the channel where the user sent their signup request
        await message.channel.send(
            "Signup successful! You can now log in using !login."
        )
        return
    await message.channel.send(
        f"An error occurred: {response.json().get('detail', 'Unknown error')}\nPlease try again."
    )


bot.run(DISCORD_TOKEN)
