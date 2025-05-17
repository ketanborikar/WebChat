import socketio

sio = socketio.Client()

user_name = input("Enter your name: ")

@sio.on("message")
def receive_message(msg):
    # Only display messages **not** sent by this user
    if not msg.startswith(f"{user_name}:"):
        print(f"\n{msg}")

sio.connect("https://webchat-s57g.onrender.com")

while True:
    msg = input(f"{user_name}: ")  # Shows name while typing
    if msg.strip():  # Prevents empty messages
        sio.send(f"{user_name}: {msg}")  # Sends message to the server
