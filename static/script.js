const socket = io("your-render-url");

function signup() {
    let username = document.getElementById("signup-username").value;
    let password = document.getElementById("signup-password").value;

    fetch('/auth/signup', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => alert(data.message));
}

function login() {
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;

    fetch('/auth/login', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => {
          if (data.access_token) {
              localStorage.setItem("token", data.access_token);
              alert("Login Successful!");
          } else {
              alert("Invalid Credentials");
          }
      });
}

socket.on("message", function(data) {
    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><strong>${data.sender}:</strong> ${data.content}</p>`;
});

function sendGroupMessage() {
    let content = document.getElementById("chat-message").value;
    socket.emit("message", { sender: "User", group: "main", content });
}
