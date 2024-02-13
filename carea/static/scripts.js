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
        visitorUserId = user_id === 2 ? 3 : 2;
        // 테스트 시 첫 번째 토큰은 '자준청', 두 번째 토큰은 '캐리아' (만료 시 재발급 후 수정)
        currentToken = user_id === 2
            ? "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA3ODQzNDQ3LCJpYXQiOjE3MDc3MzU4NzEsImp0aSI6IjUzMDcwODdmNmQ5YTQ1OGU4Mjk1MzMxODRlYzk4OWNlIiwidXNlcl9pZCI6Mn0.b4ZdKY36zLWMp9pSpXo2l9XITXTeChj0tvq2JR0htbc"
            : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA3ODQzNTQ5LCJpYXQiOjE3MDc3MzA2ODcsImp0aSI6IjNlZWQwNTlkZDJlNTRlZjViYzdlNmFjMGE2NjIzMDYwIiwidXNlcl9pZCI6M30.x4ig6GsMbC1WQdhkAL2yVaf_DejDFfxUh3vo2kBpBCU";
        await openOrCreateRoom(currentToken);
    };

    async function openOrCreateRoom(currentToken) {
        if (socket) {
            socket.close();
        }

        sortedIds = [currentUserId, visitorUserId].sort();

        currentRoomId = 1;

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
            displayMessages(messages);
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
        socket = new WebSocket(`ws://127.0.0.1:8000/ws/chats/${room_id}/?token=${currentToken}`);

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