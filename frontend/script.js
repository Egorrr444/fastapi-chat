let socket = null;
let currentUser = null;

// Функция входа
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('http://localhost:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = username;
            connectWebSocket(data.access_token);
            showChatScreen();
        } else {
            showMessage('Ошибка входа: неверный логин или пароль');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу');
    }
}

// Функция регистрации
async function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            showMessage('Регистрация успешна! Теперь войдите.');
        } else {
            showMessage('Ошибка регистрации: пользователь уже существует');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу');
    }
}

// Подключение к WebSocket
function connectWebSocket(token) {
    socket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    
    socket.onopen = () => {
        console.log('WebSocket подключен');
        document.getElementById('message-input').focus();
    };
    
    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        addMessage(message.text, message.username);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket ошибка:', error);
    };
    
    socket.onclose = () => {
        console.log('WebSocket отключен');
    };
}

// Отправка сообщения
function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    
    if (socket && text) {
        socket.send(JSON.stringify({ text }));
        input.value = '';
    }
}


// Добавление сообщения в чат
function addMessage(text, username) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = username === currentUser ? 'message my-message' : 'message other-message';
    messageDiv.innerHTML = `<strong>${username}:</strong> ${text}`;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Переключение между экранами
function showChatScreen() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('chat-screen').style.display = 'block';
    document.getElementById('current-user').textContent = currentUser;
    document.getElementById('message-input').focus();
}

function logout() {
    if (socket) {
        socket.close();
        socket = null;
    }
    currentUser = null;
    document.getElementById('chat-screen').style.display = 'none';
    document.getElementById('login-screen').style.display = 'block';
    document.getElementById('messages').innerHTML = '';
}

function showMessage(text) {
    document.getElementById('login-message').textContent = text;
    setTimeout(() => {
        document.getElementById('login-message').textContent = '';
    }, 3000);
}

// Поддержка Enter для отправки
document.getElementById('message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});