let currentUserId = null;
let currentRoomId = null;
let currentToken = null;
let socket = null;
let visitorUserId = null;
let sortedIds = null;

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    messageInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            sendMessage(currentUserId);
        }
    });

    window.loginAsUser = async (user_id) => {
        currentUserId = user_id;
        visitorUserId = user_id === 26 ? 28 : 26;
        // 테스트 시 첫 번째 토큰은 '자준청', 두 번째 토큰은 '캐리아' (만료 시 재발급 후 수정)
        currentToken = user_id === 26
            ? "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4NTMxMTA4LCJpYXQiOjE3MDg1MjM5MDgsImp0aSI6IjVlZjhkMDc3NTM1NjQ0ZTViMGRhMjJlOWVlNzMzM2ViIiwidXNlcl9pZCI6MjZ9.dAl0RLYpDkovd-waBq3CDMnH-Yi0wwxyCcjqUItWfUU"
            : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4Njk4Mjk5LCJpYXQiOjE3MDg1MjU0OTksImp0aSI6IjQ1ODlhMmNiMzFhMzQ2MDQ4ZTU2MTZmMWQyYTZhMjcwIiwidXNlcl9pZCI6Mjh9.70rSR0rzgADvkvQmu_VA0wWFVyVMIx7CYrtaF5PpJVU";
        await openOrCreateRoom(currentToken);
    };

    async function openOrCreateRoom(currentToken) {
        if (socket) {
            socket.close();
        }

        sortedIds = [currentUserId, visitorUserId].sort();

        currentRoomId = 5;

        const response = await fetch(`http://127.0.0.1:8000/chats/${currentRoomId}/messages`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + currentToken,
            }
        })
        const messages = await response.json();
        console.log(messages);
        if (response.ok) {
            displayMessages(messages.result);
        }

        setupWebSocket(currentRoomId, currentToken);

        sendBtn.onclick = () => sendMessage(currentUserId);
    }

    function displayMessages(messages) {
        chatMessages.innerHTML = '';
        messages.forEach((message) => {
            if (message.user && message.message) {
                const messageElem = document.createElement('div');
                messageElem.classList.add('message-bubble');
                messageElem.textContent = `${message.user}: ${message.message}`;

                if (message.user === currentUserId) {
                    messageElem.classList.add('sent');
                } else {
                    messageElem.classList.add('received');
                }

                chatMessages.appendChild(messageElem);
            }
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function setupWebSocket(room_id, currentToken) {
        socket = new WebSocket(`ws://127.0.0.1:8000/ws/chats/${room_id}?token=${currentToken}`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messageElem = document.createElement('div');
            messageElem.classList.add('message-bubble');
            messageElem.textContent = `${data.user_id}: ${data.message}`;

            if (data.user_id === currentUserId) {
                messageElem.classList.add('sent');
            } else {
                messageElem.classList.add('received');
            }

            chatMessages.appendChild(messageElem);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };
    }

    function sendMessage(user_id) {
        const message = messageInput.value;
        if (message) {
            const messagePayload = {
                'message': message,
            };

            socket.send(JSON.stringify(messagePayload));
            messageInput.value = '';
        }
    }
});