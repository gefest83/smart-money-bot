
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.webapp.log_buffer import get_logs, tail

templates = Jinja2Templates(directory="app/webapp/templates")

@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    recent = tail(200)
    return templates.TemplateResponse("/app/webapp/templates/logs.html" if False else "logs.html", {"request": request, "logs": recent})

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
