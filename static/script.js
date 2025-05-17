const socket = io("your-render-url");

socket.on("message", function(data) {
    displayMessage(data);
});

function sendMessage(sender, receiver, content, group) {
    socket.emit("message", { sender, receiver, content, group });
}

function toggleDrawer() {
    let drawer = document.getElementById("drawer");
    drawer.style.display = (drawer.style.display === "none") ? "block" : "none";
}
