import socketio

sio = socketio.Client()

@sio.on("message")
def receive_message(msg):
    print(f"\nReceived: {msg}")

sio.connect("http://127.0.0.1:5000")

print("Type your message and press Enter:")
while True:
    msg = input()
    sio.send(msg)
