from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal, Message

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# WebSocket接続リスト
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
            data = await websocket.receive_text()
            # DBに保存
            db = SessionLocal()
            msg = Message(sender="User", content=data)
            db.add(msg)
            db.commit()
            db.close()
            # 全員に送信
            for connection in connections:
                await connection.send_text(f"User: {data}")
    except:
        connections.remove(websocket)
