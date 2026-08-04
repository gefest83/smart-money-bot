from __future__ import annotations
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from pathlib import Path
from app.database.trades import TradeDatabase
from app.backtest.report import BacktestReport
from app.core.logger import logger, setup_logger
from app.core.config import settings
from app.exchanges.manager import ExchangeManager
from app.data.market_data import MarketData
from app.strategies.smart_money import SmartMoneyStrategy
from app.trader.executor import Executor
from app.runner.manager import start_engine, stop_engine, engine_status
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import threading

app = FastAPI(title="Smart Money Bot UI")
_db = TradeDatabase(path=settings.DATA_PATH / "trades.db")
_reporter = BacktestReport()

@app.get("/", response_class=HTMLResponse)
def index():
    html = ["<html><head><title>Smart Money Bot</title></head><body>"]
    html.append("<h1>Smart Money Bot</h1>")
    html.append("<p><a href=/backtest>Run Backtest</a> | <a href=/trades>View Trades</a> | <a href=/engine>Engine</a></p>")
    html.append("</body></html>")
    return HTMLResponse("".join(html))

@app.get("/trades", response_class=HTMLResponse)
def view_trades():
    rows = _db.get_all_trades()
    html = ["<html><head><title>Trades</title></head><body>"]
    html.append("<h2>Trades</h2>")
    html.append("<table border=1 cellpadding=6><tr><th>ID</th><th>Symbol</th><th>Side</th><th>Entry</th><th>Exit</th><th>Amount</th><th>PnL</th><th>Reason</th><th>Opened</th><th>Closed</th></tr>")
    for r in rows:
        html.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    html.append("</table>")
    html.append("<p><a href=/>Back</a></p>")
    html.append("</body></html>")
    return HTMLResponse("".join(html))

@app.get("/backtest", response_class=HTMLResponse)
def backtest_trigger():
    thread = threading.Thread(target=_run_backtest_sync, daemon=True)
    thread.start()
    return HTMLResponse("<html><body><p>Backtest started in background. <a href=/>Home</a> or <a href=/trades>View Trades</a>.</p></body></html>")

@app.get('/metrics')
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get('/engine', response_class=HTMLResponse)
def engine_page():
    st = engine_status()
    running = 'running' if st['running'] else 'stopped'
    html = [f"<html><head><title>Engine</title></head><body>"]
    html.append(f"<h2>Engine status: {running}</h2>")
    if st['running']:
        html.append('<form action="/engine/stop" method="post"><button type="submit">Stop Engine</button></form>')
    else:
        html.append('<form action="/engine/start" method="post">Mode: <select name="mode"><option value="paper">paper</option><option value="live">live</option></select> Interval(s): <input name="interval" value="10"/><button type="submit">Start Engine</button></form>')
    html.append('<p><a href="/">Home</a></p>')
    html.append('</body></html>')
    return HTMLResponse(''.join(html))

@app.post('/engine/start')
def engine_start(mode: str = Form('paper'), interval: int = Form(10)):
    start_engine(mode=mode, interval=int(interval), amount=1.0)
    return RedirectResponse('/engine', status_code=303)

@app.post('/engine/stop')
def engine_stop():
    stop_engine()
    return RedirectResponse('/engine', status_code=303)

# websocket status endpoint
@app.websocket('/ws/status')
async def ws_status(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            st = engine_status()
            await ws.send_json(st)
            await ws.receive_text()
    except WebSocketDisconnect:
        return

def _run_backtest_sync():
    setup_logger()
    logger.info("Starting backtest from web request")
    ex = ExchangeManager()
    ex.connect()
    md = MarketData(ex)
    candles = md.fetch_candles(settings.SYMBOL, settings.TIMEFRAME, limit=1000)
    strat = SmartMoneyStrategy()
    signals = strat.generate_signals(candles)
    exec = Executor()
    closed = []
    for i, c in enumerate(candles):
        price = float(c[4])
        sig = signals.get(i)
        if sig and not exec.in_position:
            exec.process_signal(sig, amount=1.0)
        ct = exec.update_price(price)
        if ct:
            for t in ct:
                _db.add_trade(t)
                closed.append(t)
    if exec.in_position:
        lp = float(candles[-1][4])
        t = exec.close_position(lp, reason="End of backtest")
        if t:
            _db.add_trade(t)
            closed.append(t)
    ex.close()
    path = _reporter.save(closed)
    logger.info(f"Backtest finished, report: {path}")
