const chatDiv = document.getElementById("chat");
const onlineUsersSpan = document.getElementById("onlineUsers");
const messageInput = document.getElementById("messageInput");
const myUsername = document.getElementById("username").value;

const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // オンラインユーザー更新
    if (data.online_users) {
        onlineUsersSpan.textContent = data.online_users.join(", ");
    }

    // メッセージ表示
    if (data.message) {
        const msgEl = document.createElement("div");
        msgEl.className = `chat-message ${data.username === myUsername ? "me" : "other"}`;
        msgEl.innerHTML = `<b>${data.username}:</b> ${data.message}`;
        chatDiv.appendChild(msgEl);

        // 少し遅らせて show クラスを追加 → ふわっと浮く
        setTimeout(() => {
            msgEl.classList.add("show");
        }, 10);

        chatDiv.scrollTop = chatDiv.scrollHeight;
    }
};

const sendMessage = () => {
    const message = messageInput.value;
    if (message) {
        ws.send(JSON.stringify({ message }));
        messageInput.value = "";
    }
};

document.getElementById("sendBtn").onclick = sendMessage;
messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});
