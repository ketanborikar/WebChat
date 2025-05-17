import asyncio
import websockets
import json
import asyncpg
import os
from datetime import datetime
from aiohttp import web  # New HTTP endpoint for health checks

# Get port from Render's environment variable
PORT = int(os.getenv("PORT", 8765))  
HTTP_PORT = 8000  # Separate port for health checks

DATABASE_URL = "postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# Active connections dictionary
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
    """Handle incoming WebSocket connections and messages."""
    try:
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

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        if websocket in connected_users:
            leave_msg = json.dumps({"type": "notification", "content": f"{connected_users[websocket]} has left the chat."})
            del connected_users[websocket]
            await asyncio.gather(*[user.send(leave_msg) for user in connected_users])

async def health_check(request):
    """Simple HTTP endpoint for Render health checks."""
    return web.Response(text="OK")

async def main():
    """Ensure WebSocket server & health check run correctly."""
    ws_server = await websockets.serve(handler, "0.0.0.0", PORT)
    http_server = web.Application()
    http_server.router.add_get("/", health_check)
    runner = web.AppRunner(http_server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    await site.start()

    print(f"WebSocket server started on port {PORT}...")
    print(f"HTTP health check running on port {HTTP_PORT}...")
    
    await asyncio.Future()  # Keeps the event loop running

if __name__ == "__main__":
    asyncio.run(main())  # Starts the event loop correctly
