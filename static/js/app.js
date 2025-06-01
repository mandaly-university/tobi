// Initialize Socket.IO connection
const socket = io();

// DOM Elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chatMessages = document.getElementById('chat-messages');
const imageForm = document.getElementById('image-form');
const videoForm = document.getElementById('video-form');
const statusIndicator = document.getElementById('status');
const activeUsersCount = document.getElementById('active-users');

// State
let isTyping = false;

// Socket.IO Event Handlers
socket.on('connect', () => {
    updateStatus(true);
    addSystemMessage('Connected to Tobi');
});

socket.on('disconnect', () => {
    updateStatus(false);
    addSystemMessage('Disconnected from Tobi');
});

socket.on('chat_response', (data) => {
    removeTypingIndicator();
    addBotMessage(data.message);
});

socket.on('typing', () => {
    if (!isTyping) {
        isTyping = true;
        addTypingIndicator();
    }
});

socket.on('stop_typing', () => {
    isTyping = false;
    removeTypingIndicator();
});

socket.on('active_users', (count) => {
    activeUsersCount.textContent = count;
});

socket.on('image_progress', (data) => {
    updateImageProgress(data.progress);
});

socket.on('image_result', (data) => {
    showImageResult(data.image_url);
});

socket.on('video_progress', (data) => {
    updateVideoProgress(data.progress);
});

socket.on('video_result', (data) => {
    showVideoResult(data.video_url);
});

// UI Functions
function updateStatus(online) {
    const statusText = online ? 'Online' : 'Offline';
    const statusColor = online ? 'text-green-500' : 'text-red-500';
    statusIndicator.innerHTML = `
        <i class="fas fa-circle ${statusColor}"></i> ${statusText}
    `;
}

function addSystemMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message system text-center text-gray-500 text-sm';
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message user fade-in';
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message bot fade-in';
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

function addTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator fade-in';
    indicator.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    chatMessages.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function updateImageProgress(progress) {
    const progressBar = document.querySelector('#image-progress .bg-green-500');
    const progressText = document.querySelector('#image-progress p');
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `Generating image... ${progress}%`;
}

function showImageResult(imageUrl) {
    const resultDiv = document.getElementById('image-result');
    const progressDiv = document.getElementById('image-progress');
    const img = resultDiv.querySelector('img');
    
    img.src = imageUrl;
    resultDiv.classList.remove('hidden');
    progressDiv.classList.add('hidden');
}

function updateVideoProgress(progress) {
    const progressBar = document.querySelector('#video-progress .bg-purple-500');
    const progressText = document.querySelector('#video-progress p');
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `Generating video... ${progress}%`;
}

function showVideoResult(videoUrl) {
    const resultDiv = document.getElementById('video-result');
    const progressDiv = document.getElementById('video-progress');
    const video = resultDiv.querySelector('video source');
    
    video.src = videoUrl;
    video.parentElement.load();
    resultDiv.classList.remove('hidden');
    progressDiv.classList.add('hidden');
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event Listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('chat_message', { message });
        addUserMessage(message);
        messageInput.value = '';
    }
});

imageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const prompt = document.getElementById('image-prompt').value.trim();
    if (prompt) {
        document.getElementById('image-result').classList.add('hidden');
        document.getElementById('image-progress').classList.remove('hidden');
        socket.emit('media_generation_request', {
            type: 'image',
            prompt: prompt
        });
    }
});

videoForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const prompt = document.getElementById('video-prompt').value.trim();
    if (prompt) {
        document.getElementById('video-result').classList.add('hidden');
        document.getElementById('video-progress').classList.remove('hidden');
        socket.emit('media_generation_request', {
            type: 'video',
            prompt: prompt
        });
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    addSystemMessage('Welcome to Tobi! How can I help you today?');
}); 