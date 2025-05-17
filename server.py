import asyncio
import websockets
import json
import asyncpg
import os
from datetime import datetime
from aiohttp import web  # HTTP server for health checks

# Get WebSocket port from Render
WS_PORT = int(os.getenv("PORT", 8765))  
# Separate HTTP health check port (Render expects HTTP for health check requests)
HTTP_PORT = 8000  

DATABASE_URL = "postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

connected_users = {}

async def save_message(sender, content):
    """Store messages in PostgreSQL."""
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO messages (sender, content, timestamp) VALUES ($1, $2, $3)", sender, content, datetime.utcnow())
    await conn.close()

async def get_chat_history():
    """Retrieve chat history from PostgreSQL."""
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT sender, content, timestamp FROM messages ORDER BY timestamp DESC LIMIT 50")
    await conn.close()
    return [{"sender": row["sender"], "content": row["content"], "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")} for row in rows]

async def handler(websocket, path):
    """Handles WebSocket connections only."""
    name = await websocket.recv()
    connected_users[websocket] = name

    join_msg = json.dumps({"type": "notification", "content": f"{name} has joined the chat."})
    await asyncio.gather(*[user.send(join_msg) for user in connected_users if user != websocket])

    history = await get_chat_history()
    await websocket.send(json.dumps({"type": "history", "messages": history}))

    async for message in websocket:
        msg_data = json.loads(message)
        sender, content = connected_users[websocket], msg_data["content"]
        await save_message(sender, content)

        msg_json = json.dumps({"type": "message", "sender": sender, "content": content})
        await asyncio.gather(*[user.send(msg_json) for user in connected_users])

async def health_check(request):
    """Simple HTTP health check for Render."""
    return web.Response(text="OK")

async def start_servers():
    """Runs both WebSocket and HTTP health check servers."""
    ws_server = await websockets.serve(handler, "0.0.0.0", WS_PORT)

    http_server = web.Application()
    http_server.router.add_get("/", health_check)
    runner = web.AppRunner(http_server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    await site.start()

    print(f"WebSocket server running on port {WS_PORT}...")
    print(f"HTTP health check running on port {HTTP_PORT}...")

    await asyncio.Future()  # Keeps event loop alive

if __name__ == "__main__":
    asyncio.run(start_servers())
