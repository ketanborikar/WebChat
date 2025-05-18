const socket = io("https://webchat-yoaw.onrender.com");

// ✅ Ensure `sendGroupMessage` is correctly defined
function sendGroupMessage() {
    let inputField = document.getElementById("chat-message");
    let content = inputField.value.trim();

    if (content !== "") {
        console.log("Sending message:", content);
        socket.emit("message", { sender: localStorage.getItem("username"), group: "main", content });

        inputField.value = ""; // ✅ Clears input field after sending
    }
}

// ✅ Allow hitting Enter to send messages
document.addEventListener("DOMContentLoaded", function() {
    let chatInput = document.getElementById("chat-message");
    
    if (chatInput) {
        chatInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendGroupMessage();
            }
        });
    } else {
        console.log("Error: chat-message element not found.");
    }
});

// ✅ Popup menu for switching between private chats and group chat
function toggleChatMenu() {
    let menu = document.getElementById("chat-switch-menu");
    menu.classList.toggle("show-chat-menu");

    menu.innerHTML = "<h3>Switch Chat</h3>";

    // ✅ Add Group Chat option
    let groupChatBtn = document.createElement("button");
    groupChatBtn.innerText = "Group Chat";
    groupChatBtn.onclick = () => switchTab("group");
    menu.appendChild(groupChatBtn);

    // ✅ Fetch private chats dynamically
    fetch("https://webchat-yoaw.onrender.com/private-chats")
    .then(response => response.json())
    .then(chats => {
        chats.forEach(user => {
            let userChatBtn = document.createElement("button");
            userChatBtn.innerText = user.username;
            userChatBtn.onclick = () => switchTab(user.username);
            menu.appendChild(userChatBtn);
        });
    });
}

// ✅ Popup menu for displaying online users
function toggleOnlineUsers() {
    let menu = document.getElementById("online-users-menu");
    menu.classList.toggle("show-users-menu");

    menu.innerHTML = "<h3>Online Users</h3><ul id='online-users'></ul>";

    fetch("https://webchat-yoaw.onrender.com/online-users")
    .then(response => response.json())
    .then(users => {
        let userList = document.getElementById("online-users");
        userList.innerHTML = ""; // Clear previous list

        users.forEach(user => {
            let userItem = document.createElement("li");
            userItem.innerText = user.username;
            userList.appendChild(userItem);
        });
    });
}
