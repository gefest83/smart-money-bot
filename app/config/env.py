import os

from pathlib import Path
from dotenv import load_dotenv

from loguru import logger



# Загружаем .env из корня проекта

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"


load_dotenv(
    ENV_FILE
)



class Environment:


    def __init__(self):

        self.exchange = os.getenv(
            "EXCHANGE",
            "BINANCE"
        )


        self.api_key = os.getenv(
            "API_KEY",
            ""
        )


        self.api_secret = os.getenv(
            "API_SECRET",
            ""
        )


        self.testnet = (

            os.getenv(
                "TESTNET",
                "false"
            )
            .lower()
            == "true"

        )



        self.live_enabled = (

            os.getenv(
                "ENABLE_LIVE_ORDERS",
                "false"
            )
            .lower()
            == "true"

        )



        logger.info(
            f"""
================ ENVIRONMENT ================

Exchange:
{self.exchange}

API Key:
{"LOADED" if self.api_key else "NOT FOUND"}

Secret:
{"LOADED" if self.api_secret else "NOT FOUND"}

Testnet:
{self.testnet}

Live Orders:
{self.live_enabled}

==============================================
"""
        )



    def has_keys(self):

        return bool(
            self.api_key
            and
            self.api_secret
        )



env = Environment()