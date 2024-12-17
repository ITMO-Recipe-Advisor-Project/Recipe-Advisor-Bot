from dotenv import dotenv_values

def get_config():
    """
    Loads configuration values from a `.env` file.

    :return: A dictionary containing:
             - BOT_TOKEN: Token for authenticating the Telegram bot.
             - API_URL: URL of the recipe processing service.
             - GIPHY_API_URL: Base URL for the GIPHY API to fetch GIFs.
             - GIPHY_API_KEY: API key for authenticating requests to GIPHY.
             - GIF_QUERY: Search query used to fetch specific GIFs (e.g., 'chef').
             - REQUEST_TIMEOUT: Timeout value (in seconds) for HTTP requests.
    """
    env_vars = dotenv_values("env/.env")
    return {
        "BOT_TOKEN": env_vars["BOT_TOKEN"],
        "API_URL": env_vars["API_URL"],
        "GIPHY_API_URL": env_vars["GIPHY_API_URL"],
        "GIPHY_API_KEY": env_vars["GIPHY_API_KEY"],
        "GIF_QUERY": env_vars["GIF_QUERY"],
        "REQUEST_TIMEOUT": float(env_vars["REQUEST_TIMEOUT"])
    }
