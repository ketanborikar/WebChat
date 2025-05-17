const socket = io("https://webchat-yoaw.onrender.com");

// Confirm WebSocket connection
socket.on("connect", function() {
    console.log("WebSocket connected successfully!");
});

function sendGroupMessage() {
    let content = document.getElementById("chat-message").value;

    // Debugging log before sending
    console.log("Sending message:", content);

    socket.emit("message", { sender: "Ketan", group: "main", content }, (response) => {
        console.log("Server response:", response);  // ✅ This should no longer be undefined
    });

    // Debugging log to confirm receipt from server
    socket.on("message", function(data) {
        console.log("Message received from server:", data);
    });

    socket.on("error", function(error) {
        console.log("Error from server:", error);
    });
}
