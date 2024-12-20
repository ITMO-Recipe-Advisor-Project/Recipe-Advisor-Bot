import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import httpx
from app.config import get_config

config = get_config()

BOT_TOKEN = config["BOT_TOKEN"]
API_URL = config["API_URL"]
GIPHY_API_URL = config["GIPHY_API_URL"]
GIPHY_API_KEY = config["GIPHY_API_KEY"]
GIF_QUERY = config["GIF_QUERY"]
REQUEST_TIMEOUT = config["REQUEST_TIMEOUT"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_last_queries = {}
gif_urls = []


def create_more_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="More Recipes", callback_data="more_recipes")]]
    )


async def fetch_gifs():
    """Requests 25 gifs from the GIPHY API and saves them to a list."""
    global gif_urls
    params = {
        "api_key": GIPHY_API_KEY,
        "q": GIF_QUERY,
        "limit": 25,
        "offset": 0,
        "rating": "g",
        "lang": "en",
        "bundle": "messaging_non_clips",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GIPHY_API_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                gif_urls = [item["images"]["original"]["url"] for item in data.get("data", [])]
                print(f"Fetched {len(gif_urls)} GIFs successfully.")
            else:
                print(f"Failed to fetch GIFs. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching GIFs: {e}")


@dp.message(Command("start"))
async def start_handler(message: Message):
    """Handles the /start command."""
    warning_message = (
        "*⚠️ Warning:*\n"
        "_The server uses Runpod serverless solution with a cold start to process embedding inference requests based on "
        "user queries._ As a result, responses might take up to *30 seconds*. This decision was made due to server "
        "limitations, and we apologize for any inconvenience."
    )
    await message.reply(warning_message, parse_mode="Markdown")
    await message.answer("Hello! Send me a query with the ingredients you'd like, and I'll help you find some recipes.")


@dp.message()
async def handle_message(message: Message):
    """Handles user text input."""
    user_query = message.text
    user_id = message.from_user.id

    await message.answer("Request in process, please wait a moment ...")

    if gif_urls:
        gif_url = random.choice(gif_urls)
        await message.answer_animation(gif_url)

    try:
        timeout = httpx.Timeout(REQUEST_TIMEOUT)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(API_URL, json={"query": user_query})

            if response.status_code == 200:
                response_data = response.json()

                if "message" in response_data:
                    await message.answer(response_data["message"])
                    recipes = response_data.get("recipes", [])

                    if recipes:
                        user_last_queries[user_id] = user_query

                        for recipe in recipes:
                            await message.answer(recipe)

                        await message.answer("Would you like to see more recipes?", reply_markup=create_more_button())
                    else:
                        await message.answer("No recipes found for your query.")
                else:
                    await message.answer("The server returned an unexpected response.")
            else:
                await message.answer(f"Server error: {response.status_code}")
    except httpx.RequestError as e:
        await message.answer(f"Failed to connect to the server. Error: {e}")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")


@dp.callback_query(lambda c: c.data == "more_recipes")
async def more_recipes_callback(callback_query: types.CallbackQuery):
    """Handles the 'More Recipes' button callback."""
    user_id = callback_query.from_user.id

    if user_id in user_last_queries:
        last_query = user_last_queries[user_id]
        await callback_query.answer("")

        await callback_query.message.answer("Searching for more recipes with the same ingredients...")

        try:
            timeout = httpx.Timeout(REQUEST_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(API_URL, json={"query": last_query})

                if response.status_code == 200:
                    response_data = response.json()
                    recipes = response_data.get("recipes", [])

                    if recipes:
                        for recipe in recipes:
                            await callback_query.message.answer(recipe)
                        await callback_query.message.answer(
                            "Would you like to see even more recipes?", reply_markup=create_more_button()
                        )
                    else:
                        await callback_query.message.answer("No more recipes found for your query.")
                else:
                    await callback_query.message.answer(f"Server error: {response.status_code}")
        except httpx.RequestError as e:
            await callback_query.message.answer(f"Failed to connect to the server. Error: {e}")
        except Exception as e:
            await callback_query.message.answer(f"An error occurred: {e}")
    else:
        await callback_query.answer("No previous search found.")
        await callback_query.message.answer("Please send a new list of ingredients to search for recipes.")


async def main():
    """Starts the bot."""
    await fetch_gifs()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
