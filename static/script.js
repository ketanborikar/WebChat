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

              alert("Login Successful!");

              // Hide login/signup and show chat UI
              document.getElementById("auth").style.display = "none";
              document.getElementById("chat-ui").style.display = "block";
          } else {
              alert("Invalid Credentials");
          }
      });
}

function switchTab(tab) {
    let chatTitle = document.getElementById("chat-title");
    let chatBox = document.getElementById("chat-box");

    if (tab === "group") {
        chatTitle.innerText = "Group Chat";
    } else {
        chatTitle.innerText = "Private Chat";
    }

    chatBox.innerHTML = ""; // Clear chat window when switching tabs
}

function sendGroupMessage() {
    let content = document.getElementById("chat-message").value;
    console.log("Sending message:", content);

    socket.emit("message", { sender: localStorage.getItem("username"), group: "main", content }, (response) => {
        console.log("Server response:", response);
    });

    socket.on("message", function(data) {
        console.log("Message received from server:", data);
        let chatBox = document.getElementById("chat-box");
        chatBox.innerHTML += `<p><strong>${data.sender}:</strong> ${data.content}</p>`;
    });

    socket.on("error", function(error) {
        console.log("Error from server:", error);
    });
}

function toggleDrawer() {
    let drawer = document.getElementById("drawer");
    drawer.style.display = (drawer.style.display === "none") ? "block" : "none";
}

function toggleTabs() {
    let tabs = document.getElementById("tabs");
    tabs.classList.toggle("show-tabs"); // Toggle visibility
}
