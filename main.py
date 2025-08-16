from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal, Message
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

connections = []

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)  # {"username": "...", "message": "..."}
            username = data.get("username", "Guest")
            message = data.get("message", "")

            # DBに保存
            db = SessionLocal()
            msg = Message(sender=username, content=message)
            db.add(msg)
            db.commit()
            db.close()

            # 全員に送信
            for connection in connections:
                await connection.send_text(json.dumps({"username": username, "message": message}))
    except WebSocketDisconnect:
        connections.remove(websocket)
