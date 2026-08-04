from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    """
    Основная конфигурация Smart Money Bot.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


    APP_NAME: str = "Smart Money Bot"
    VERSION: str = "0.1.0"


    # Биржа
    EXCHANGE: str = Field(default="binance")
    MARKET: str = Field(default="futures")


    # Торговая пара
    SYMBOL: str = Field(
        default="BTC/USDT"
    )

    TIMEFRAME: str = Field(
        default="15m"
    )


    # API Binance
    API_KEY: str = ""

    API_SECRET: str = ""

    API_PASSWORD: str = ""


    # Режим работы
    TESTNET: bool = True


    # ВАЖНО
    # False = только симуляция
    # True  = реальные ордера
    LIVE_ORDERS: bool = False


    # Paper trading баланс
    PAPER_BALANCE: float = 10000.0


    # Риск
    LEVERAGE: int = 10

    RISK_PERCENT: float = 1.0


    # Пути
    DATA_PATH: Path = Path(
        "data"
    )

    LOG_PATH: Path = Path(
        "logs"
    )


settings = Settings()