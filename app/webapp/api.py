from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.webapp.log_buffer import tail
from app.runner import manager as runner_manager
from app.database.trades import TradeDatabase
from app.core.config import settings

app = FastAPI()

templates = Jinja2Templates(directory="app/webapp/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    recent = tail(200)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": recent})


@app.get('/logs/stream')
async def logs_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            for line in tail(50):
                await websocket.send_text(line)
            await websocket.receive_text()
    except WebSocketDisconnect:
        return


@app.get("/engine", response_class=HTMLResponse)
def engine_page(request: Request):
    status = runner_manager.engine_status()
    return templates.TemplateResponse(
        "engine.html",
        {"request": request, "status": status, "running": status.get("running")},
    )


@app.post("/engine/start")
async def engine_start(
    mode: str = Form("paper"), interval: int = Form(10), amount: float = Form(1.0)
):
    runner_manager.start_engine(mode=mode, interval=interval, amount=amount)
    return RedirectResponse(url="/engine", status_code=303)


@app.post("/engine/stop")
async def engine_stop():
    runner_manager.stop_engine()
    return RedirectResponse(url="/engine", status_code=303)


@app.get("/trades", response_class=HTMLResponse)
def trades_page(request: Request):
    db = TradeDatabase(path=settings.DATA_PATH / "trades.db")
    trades = db.get_all_trades()
    return templates.TemplateResponse("trades.html", {"request": request, "trades": trades})
