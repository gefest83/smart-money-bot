# Smart Money Bot

Простой прототип бэктестера и бумажного трейдера для криптовалютной торговли.
Он собирает исторические свечи, генерирует торговые сигналы на основе простой стратегии
скользящих средних и эмулирует открытие/закрытие позиций. Закрытые сделки сохраняются в SQLite.

## Требования

- Python 3.10+
- ccxt
- python-dotenv
- loguru
- pydantic
- pydantic-settings

## Установка

```bash
python -m pip install -r requirements.txt
```

## Настройка

Скопируйте файл `.env.example` в `.env` и заполните нужные параметры.

```bash
copy .env.example .env
```

## Запуск

```bash
python main.py
```

## Бэктест

```bash
python backtest.py
```

## Результаты

- `data/trades.db` — база со всеми закрытыми сделками.
- `reports/trades.csv` — CSV-отчет по совершенным сделкам.

## Структура

- `main.py` — точка входа приложения.
- `backtest.py` — корневой скрипт для запуска бэктеста.
- `app/exchanges/manager.py` — загрузка цены и свечей через CCXT.
- `app/executor/paper.py` — симуляция бумажной торговли.
- `app/risk/manager.py` — расчет размера позиции.
- `app/strategies/simple.py` — простая стратегия для генерации сигналов.
- `app/models/` — модели данных для сделок, позиций и сигналов.
- `app/database/trades.py` — сохранение сделок в SQLite.
- `app/backtest/report.py` — экспорт истории в CSV.
