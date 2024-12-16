import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import httpx
from app.config import get_config


BOT_TOKEN = get_config()['BOT_TOKEN']
API_URL = "http://recipe-llm-service:8080/process"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    """Handles the /start command."""
    await message.answer("Hello! Send me a list of ingredients, and I'll suggest a recipe.")

@dp.message()
async def handle_message(message: Message):
    """Handles user text input."""
    await message.answer("Request in process, please wait a moment ...")

    user_query = message.text
    try:
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(API_URL, json={"query": user_query})

            if response.status_code == 200:
                response_data = response.json()

                if "message" in response_data or "recipes" in response_data["message"]:
                    await message.answer(response_data["message"])
                    for recipe in response_data.get("recipes", []):
                        await message.answer(recipe)
                else:
                    await message.answer("The server returned an unexpected response.")
            else:
                await message.answer(f"Server error: {response.status_code}")
    except httpx.RequestError as e:
        await message.answer(f"Failed to connect to the server. Error: {e}")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")

async def main():
    """Starts the bot."""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
