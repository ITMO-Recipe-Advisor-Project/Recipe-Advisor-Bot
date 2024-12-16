from dotenv import dotenv_values


def get_config():
    """
    Loads configuration values from a `.env` file.

    :return: A dictionary containing:
             - OPENAI_API_KEY: API key for openai authentication.
    """

    env_vars = dotenv_values("env/.env")
    return {
        "BOT_TOKEN": env_vars["BOT_TOKEN"],

    }
