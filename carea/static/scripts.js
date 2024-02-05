let currentUserId = null;
let currentRoomId = null;
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
        visitorUserId = user_id === 1 ? 2 : 1;
        await openOrCreateRoom();
    };

    async function openOrCreateRoom() {
        if (socket) {
            socket.close();
        }

        sortedIds = [currentUserId, visitorUserId].sort();

        /*const response = await fetch('http://127.0.0.1:8000/chats/rooms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                helped: sortedIds[0],
                helper: sortedIds[1],
                help: 1
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }*/

        currentRoomId = 1;

        const response = await fetch(`http://127.0.0.1:8000/chats/${currentRoomId}/messages`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        const messages = await response.json();
        console.log(messages);
        if (response.ok) {
            displayMessages(messages);
        }

        setupWebSocket(currentRoomId);

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

    function setupWebSocket(room_id) {
        socket = new WebSocket(`ws://127.0.0.1:8000/ws/chats/${room_id}/`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messageElem = document.createElement('div');
            messageElem.classList.add('message-bubble');
            messageElem.textContent = `${data.sender_id}: ${data.message}`;

            if (data.sender_id === currentUserId) {
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
                'sender_id': user_id,
                'message': message,
                'helped_id': sortedIds[0],
                'helper_id': sortedIds[1],
                'help_id': 1,
            };

            socket.send(JSON.stringify(messagePayload));
            messageInput.value = '';
        }
    }
});