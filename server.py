import asyncio
import websockets
import json
import asyncpg
import os
from datetime import datetime

# Get port from Render's environment variable
PORT = int(os.getenv("PORT", 8765))  

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
    """Handle incoming connections and messages."""
    try:
        # Receive initial handshake with username
        name = await websocket.recv()
        connected_users[websocket] = name

        # Notify users of the new connection
        join_msg = json.dumps({"type": "notification", "content": f"{name} has joined