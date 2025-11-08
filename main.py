from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, Message
import json, os
from dotenv import load_dotenv

load_dotenv()

# .envからユーザー情報を読み込む
CHAT_CREDENTIALS = json.loads(os.getenv("CHAT_CREDENTIALS", "{}"))

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket接続管理
connections: dict[str, WebSocket] = {}

async def broadcast_message(message: dict):
    """全員にメッセージを送信"""
    for conn in connections.values():
        await conn.send_text(json.dumps(message))

async def broadcast_online_users():
    """オンラインユーザーリストを全員に送信"""
    users = list(connections.keys())
    for conn in connections.values():
        await conn.send_text(json.dumps({"type": "online_users", "users": users}))

@app.get("/", response_class=HTMLResponse)
async def root(session_id: str = Cookie(None)):
    if session_id not in CHAT_CREDENTIALS:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/chat")

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in CHAT_CREDENTIALS and password == CHAT_CREDENTIALS[username]:
        response = RedirectResponse(url="/chat", status_code=302)
        response.set_cookie(key="session_id", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "ログインIDかパスワードが違います"})

@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request, session_id: str = Cookie(None)):
    if session_id not in CHAT_CREDENTIALS:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "username": session_id})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Cookie(None)):
    if session_id not in CHAT_CREDENTIALS:
        await websocket.close()
        return

    await websocket.accept()
    connections[session_id] = websocket

        # オンラインユーザーを全員に通知
    async def broadcast_users():
        online_users = list(connections.keys())
        for ws in connections.values():
            await ws.send_text(json.dumps({"online_users": online_users}))

    # 接続したらオンラインユーザーリストを全員に送信
    await broadcast_users()

    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            message = data.get("message", "")

            # DBに保存
            db = SessionLocal()
            msg = Message(sender=session_id, content=message)
            db.add(msg)
            db.commit()
            db.close()

            # 全員に送信
            for ws in connections.values():
                await ws.send_text(json.dumps({
                    "username": session_id,
                    "message": message,
                    "online_users": list(connections.keys())
                }))
    except WebSocketDisconnect:
        connections.pop(session_id, None)
        await broadcast_users()
