# Smart Money Bot

Smart Money Bot — модульный trading bot для paper бэктеста и live (testnet) торговли.

Особенности
- Поддержка нескольких бирж через ccxt: Binance, Bybit, OKX, BingX, MEXC (spot и futures)
- Smart Money стратегия, портированная из Pine Script (pivot/CHoCH, ATR-based TP/SL)
- Режимы: backtest, paper, live (testnet recommended), web UI
- Trading engine с daemon-режимом: мониторинг каждые 10s, авт. открытие/закрытие позиций, частичные TP
- Хранение сделок в SQLite и экспорт в CSV
- FastAPI веб-интерфейс для просмотра сделок и запуска бэктеста
- Docker + docker-compose и CI (pytest) для быстрого развёртывания

Быстрый старт

1) Клонировать репозиторий и перейти в папку:

```bash
git clone https://github.com/gefest83/smart-money-bot.git
cd smart-money-bot
```

2) Скопировать .env и заполнить при необходимости (пример в .env):

```bash
copy .env .env.local
# или вручную отредактируйте .env
```

3) Установить зависимости и запустить в режиме paper:

```bash
python -m pip install -r requirements.txt
python main.py --mode paper
```

Запуск веб-интерфейса

```bash
python main.py --mode web
# Web UI будет доступен на http://0.0.0.0:8000
```

Запуск в Docker (рекомендуется для 24/7)

```bash
docker build -t smart-money-bot:latest .
docker run -d --name smart-money-bot -p 8000:8000 --env-file .env smart-money-bot:latest
```

Или с docker-compose:

```bash
docker-compose up -d --build
```

CI

GitHub Actions настроен для запуска pytest при PR и push.

Файлы и архитектура

```
smart-money-bot/
├── app/
│   ├── core/ (config, logger)
│   ├── exchanges/ (ccxt wrapper)
│   ├── strategies/ (smart_money port)
│   ├── trader/ (executor, position manager)
│   ├── runner/ (engine daemon)
│   ├── webapp/ (FastAPI)
│   └── database/ (SQLite persistence)
├── backtest/
├── main.py
├── Dockerfile
├── docker-compose.yml
└── .env
```

Дальше
- Вы можете подключить live API-ключи в .env для работы с биржами (используйте testnet если доступно).
- Рекомендую настроить supervisor/systemd или Docker swarm для постоянной работы 24/7.

Если нужно, настрою systemd unit, docker-compose production файл или мониторинг (Prometheus + Grafana). Сообщите, что предпочтительнее.
