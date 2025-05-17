import socketio

# Create a SocketIO client
sio = socketio.Client()

# Ask the user for their name
user_name = input("Enter your name: ")

@sio.on("message")
def receive_message(msg):
    print(f"\n{msg}")  # Display received messages

# Connect to the WebSocket server
sio.connect("https://webchat-s57g.onrender.com")

# Main loop for sending messages
print("Type your message and press Enter:")
while True:
    msg = input()
    sio.send(f"{user_name}: {msg}")  # Send message with user's name
