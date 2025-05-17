document.addEventListener("DOMContentLoaded", function() {
    let loginField = document.getElementById("login-password");
    let signupField = document.getElementById("signup-password");
    let chatInput = document.getElementById("chat-message");

    console.log("DOM fully loaded, checking elements...");

    // Ensure each element exists before adding event listeners
    if (loginField) {
        console.log("Login field found, adding event listener...");
        loginField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                login();
            }
        });
    } else {
        console.log("Error: login-password element not found.");
    }

    if (signupField) {
        console.log("Signup field found, adding event listener...");
        signupField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                signup();
            }
        });
    } else {
        console.log("Error: signup-password element not found.");
    }

    if (chatInput) {
        console.log("Chat input found, adding event listener...");
        chatInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendGroupMessage();
            }
        });
    } else {
        console.log("Error: chat-message element not found.");
    }
});

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

function showNotification(message) {
    let notif = document.getElementById("notification");
    notif.innerText = message;
    notif.style.display = "block";

    setTimeout(() => {
        notif.style.display = "none";
    }, 3000);
}

function sendGroupMessage() {
    let inputField = document.getElementById("chat-message");
    let content = inputField.value;

    if (content.trim() !== "") {
        socket.emit("message", { sender: localStorage.getItem("username"), group: "main", content });
        inputField.value = ""; // ✅ Clears input after sending
    }
}

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
