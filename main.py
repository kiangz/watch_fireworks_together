from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json

app = FastAPI()

# 全局连接列表
active_connections: List[WebSocket] = []

# 弹幕存储列表（最多保留10条）
danmaku_history = []
MAX_DANMAKU = 10

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/fireworks", response_class=HTMLResponse)
def fireworks():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"新客户端连接，当前连接数: {len(active_connections)}")
    
    # 发送历史弹幕给新连接的客户端
    await websocket.send_text(json.dumps({
        "type": "danmaku_history",
        "danmakus": danmaku_history
    }))
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"接收到消息: {data}")
            
            # 将新弹幕添加到历史列表
            if len(danmaku_history) >= MAX_DANMAKU:
                danmaku_history.pop(0)  # 移除最早的弹幕
            danmaku_history.append(data)
            
            # 广播消息给所有连接的客户端
            for connection in active_connections:
                await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"客户端断开连接，当前连接数: {len(active_connections)}")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        active_connections.remove(websocket)

