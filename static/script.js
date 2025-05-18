const socket = io("https://webchat-yoaw.onrender.com");

document.addEventListener("DOMContentLoaded", function() {
    let loginField = document.getElementById("login-password");
    let signupField = document.getElementById("signup-password");
    let chatInput = document.getElementById("chat-message");
    let loginButton = document.querySelector("#auth button[onclick='login()']");
    let signupButton = document.querySelector("#auth button[onclick='signup()']");

    console.log("DOM fully loaded, checking elements...");

    if (loginField) {
        loginField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                login();
            }
        });
    }

    if (signupField) {
        signupField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                signup();
            }
        });
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendGroupMessage();
            }
        });
    }

    if (loginButton) {
        loginButton.addEventListener("click", login);
    } else {
        console.log("Error: Login button not found.");
    }

    if (signupButton) {
        signupButton.addEventListener("click", signup);
    } else {
        console.log("Error: Signup button not found.");
    }
});

function login() {
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;

    let loadingSpinner = document.getElementById("loading");

    if (loadingSpinner) {
        loadingSpinner.style.display = "block"; // ✅ Show spinner if it exists
    } else {
        console.log("Error: 'loading' element not found."); // ✅ Debugging log
    }

    fetch("https://webchat-yoaw.onrender.com/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
      .then(data => {
          if (loadingSpinner) {
              loadingSpinner.style.display = "none"; // ✅ Hide spinner after login
          }

          if (data.access_token) {
              localStorage.setItem("token", data.access_token);
              localStorage.setItem("username", username);

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

function sendGroupMessage() {
    let inputField = document.getElementById("chat-message");
    let content = inputField.value.trim();

    if (content !== "") {
        console.log("Sending message:", content);
        socket.emit("message", { sender: localStorage.getItem("username"), group: "main", content });

        inputField.value = ""; // ✅ Clears input field after sending
    }
}
