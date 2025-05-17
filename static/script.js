const socket = io("https://webchat-yoaw.onrender.com");

// Confirm WebSocket connection
socket.on("connect", function() {
    console.log("WebSocket connected successfully!");
});

function signup() {
    let username = document.getElementById("signup-username").value;
    let password = document.getElementById("signup-password").value;

    fetch("https://webchat-yoaw.onrender.com/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => alert(data.message));
}

function login() {
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;

    fetch("https://webchat-yoaw.onrender.com/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => {
          if (data.access_token) {
              localStorage.setItem("token", data.access_token);
              localStorage.setItem("username", username);

              showNotification("Login Successful!");

              document.getElementById("auth").style.display = "none";
              document.getElementById("chat-ui").style.display = "block";
          }
      });
}

function showNotification(message) {
    let notif = document.getElementById("notification");
    notif.innerText = message;
    notif.style.display = "block";

    setTimeout(() => {
        notif.style.display = "none";
    }, 3000);
}

function switchTab(tab) {
    let chatTitle = document.getElementById("chat-title");
    let chatBox = document.getElementById("chat-box");

    chatTitle.innerText = tab === "group" ? "Group Chat" : tab;
    chatBox.innerHTML = ""; // Clear chat when switching
}

function sendGroupMessage() {
    let inputField = document.getElementById("chat-message");
    let content = inputField.value;

    if (content.trim() !== "") {
        socket.emit("message", { sender: localStorage.getItem("username"), group: "main", content });
        inputField.value = ""; // ✅ Clears input after sending
    }
}

document.getElementById("chat-message").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendGroupMessage();
    }
});

document.getElementById("login-password").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        login();
    }
});

document.getElementById("signup-password").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        signup();
    }
});

function toggleTabs() {
    let tabs = document.getElementById("tabs");
    tabs.innerHTML = "";
    tabs.classList.toggle("show-tabs");

    let groupChatBtn = document.createElement("button");
    groupChatBtn.innerText = "Group Chat";
    groupChatBtn.onclick = () => switchTab("group");
    tabs.appendChild(groupChatBtn);

    fetch("https://webchat-yoaw.onrender.com/users")
    .then(response => response.json())
    .then(users => {
        users.forEach(user => {
            let userChatBtn = document.createElement("button");
            userChatBtn.innerText = user.username;
            userChatBtn.onclick = () => switchTab(user.username);
            tabs.appendChild(userChatBtn);
        });
    });
}
