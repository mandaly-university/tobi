document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');
  const fileUpload = document.getElementById('file-upload');
  const uploadButton = document.getElementById('upload-button');
  const themeToggle = document.getElementById('theme-toggle');
  const loginButton = document.getElementById('login-button');
  const logoutButton = document.getElementById('logout-button');
  const loginModal = document.getElementById('login-modal');
  const googleSignInButton = document.getElementById('google-signin');
  const closeLoginModal = loginModal.querySelector('.close-button');
  const usageCounter = document.getElementById('usage-counter');

  // Theme
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
  }
  setTheme(localStorage.getItem('theme') || 'light');
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    setTheme(current === 'light' ? 'dark' : 'light');
  });

  // Myanmar responses
  const responses = {
    en: {
      greeting: "Hello! I'm your professional programming assistant. How can I help you today?",
      help: "I'm here to help with programming questions, file uploads, and more!",
      file: "You can upload a file using the 📎 button.",
      signedin: "You are now signed in.",
      signedout: "You have been logged out.",
      fallback: "I'm here to help with programming questions, file uploads, and more!"
    },
    my: {
      greeting: "မင်္ဂလာပါ! ကျွန်တော်က သင့်ရဲ့ programming အကူအညီပေးသူပါ။ ဘာကူညီပေးရမလဲ။",
      help: "Programming, ဖိုင်တင်ခြင်းနဲ့ မေးခွန်းများကို မြန်မာလို ဖြေပြပေးနိုင်ပါတယ်။",
      file: "📎 ခလုတ်နဲ့ ဖိုင်တင်နိုင်ပါတယ်။",
      signedin: "သင်ဝင်ရောက်ပြီးပါပြီ။",
      signedout: "သင်ထွက်ပြီးပါပြီ။",
      fallback: "Programming, ဖိုင်တင်ခြင်းနဲ့ မေးခွန်းများကို မြန်မာလို ဖြေပြပေးနိုင်ပါတယ်။"
    }
  };

  let currentLanguage = 'en';
  // Prompt for OpenAI API key if not set
  let OPENAI_API_KEY = localStorage.getItem('openai_api_key') || '';
  if (!OPENAI_API_KEY) {
    const key = prompt('Enter your OpenAI API key:');
    if (key) {
      localStorage.setItem('openai_api_key', key);
      OPENAI_API_KEY = key;
    } else {
      alert('OpenAI API key is required to use Tobi.');
      return;
    }
  }
  let conversationHistory = [
    { role: 'system', content: "You are Tobi, a helpful AI assistant. Introduce yourself as Tobi. Reply in Myanmar if the user speaks Myanmar, otherwise reply in English." }
  ];

  function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Usage limit for non-logged-in users: 5 hours per day
  const USAGE_LIMIT_SECONDS = 5 * 60 * 60; // 5 hours
  function getTodayKey() {
    const today = new Date().toISOString().split('T')[0];
    return `usage_${today}`;
  }
  function getUsage() {
    return parseInt(localStorage.getItem(getTodayKey()) || '0', 10);
  }
  function setUsage(seconds) {
    localStorage.setItem(getTodayKey(), seconds.toString());
  }
  function isLoggedIn() {
    return !!localStorage.getItem('userInfo');
  }
  let usageStart = null;
  function startUsageTimer() {
    if (isLoggedIn()) return;
    usageStart = Date.now();
  }
  function stopUsageTimer() {
    if (isLoggedIn() || usageStart === null) return;
    const elapsed = Math.floor((Date.now() - usageStart) / 1000);
    setUsage(getUsage() + elapsed);
    usageStart = null;
  }
  function checkUsageLimit() {
    if (isLoggedIn()) return false;
    return getUsage() >= USAGE_LIMIT_SECONDS;
  }
  function blockInputIfLimited() {
    if (checkUsageLimit()) {
      userInput.disabled = true;
      sendButton.disabled = true;
      addMessage('Usage limit reached: You can use Tobi for up to 5 hours per day without logging in. Please log in or come back tomorrow.', false);
    } else {
      userInput.disabled = false;
      sendButton.disabled = false;
    }
  }
  // Start/stop timer on focus/blur
  userInput.addEventListener('focus', startUsageTimer);
  userInput.addEventListener('blur', stopUsageTimer);
  window.addEventListener('beforeunload', stopUsageTimer);
  // Check limit before sending
  sendButton.addEventListener('click', () => {
    stopUsageTimer();
    if (checkUsageLimit()) {
      blockInputIfLimited();
      return;
    }
    startUsageTimer();
  }, true);
  // Check on load
  blockInputIfLimited();
  // When user logs in, remove limit
  logoutButton.addEventListener('click', blockInputIfLimited);
  loginButton.addEventListener('click', () => {
    setTimeout(blockInputIfLimited, 1000);
  });

  sendButton.addEventListener('click', handleUserInput);
  userInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') handleUserInput();
  });

  async function handleUserInput() {
    const message = userInput.value.trim();
    if (!message) return;
    userInput.value = '';
    addMessage(message, true);
    conversationHistory.push({ role: 'user', content: message });

    // Check for creator/creation date question
    if (/who.*(created|made|developer|author)|creator|who.*tobi|when.*created|creation date|who is your creator|who made you|who developed you|who is your author/i.test(message)) {
      const creatorMsg = 'Tobi is created by Kyaw Swar Aung (University of Yadanabon, Mandalay, Myanmar) Physics Final Year Student and created in 6-2-2025.';
      addMessage(creatorMsg, false);
      conversationHistory.push({ role: 'assistant', content: creatorMsg });
      return;
    }

    addMessage('...', false); // Loading indicator
    const botResponse = await getOpenAIResponse();
    // Remove loading indicator
    const lastBotMsg = chatMessages.querySelector('.bot-message:last-child');
    if (lastBotMsg) lastBotMsg.remove();
    addMessage(botResponse, false);
    conversationHistory.push({ role: 'assistant', content: botResponse });
  }

  async function getOpenAIResponse() {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: conversationHistory,
          temperature: 0.7
        })
      });
      const data = await response.json();
      if (data.choices && data.choices[0] && data.choices[0].message) {
        return data.choices[0].message.content.trim();
      } else {
        return "Sorry, I couldn't get a response from OpenAI.";
      }
    } catch (e) {
      return "Sorry, there was an error connecting to OpenAI.";
    }
  }

  // File upload
  uploadButton.addEventListener('click', () => fileUpload.click());
  fileUpload.addEventListener('change', e => {
    const file = e.target.files[0];
    if (file) {
      addMessage(`File uploaded: ${file.name} (${formatFileSize(file.size)})`);
      fileUpload.value = '';
    }
  });
  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  // Google Sign-In
  loginButton.addEventListener('click', () => {
    loginModal.classList.add('active');
    loginModal.style.display = 'flex';
    google.accounts.id.renderButton(
      googleSignInButton,
      { theme: 'outline', size: 'large', width: '100%', text: 'signin_with', shape: 'rectangular', logo_alignment: 'left' }
    );
  });
  closeLoginModal.addEventListener('click', () => {
    loginModal.classList.remove('active');
    loginModal.style.display = 'none';
  });
  function handleGoogleSignIn(response) {
    const responsePayload = jwt_decode(response.credential);
    const userInfo = {
      name: responsePayload.name,
      email: responsePayload.email,
      picture: responsePayload.picture,
      token: response.credential
    };
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    updateUIForLoggedInUser(userInfo);
    loginModal.classList.remove('active');
    loginModal.style.display = 'none';
    addMessage(`Welcome, ${userInfo.name}! You are now signed in.`);
  }
  function updateUIForLoggedInUser(userInfo) {
    loginButton.style.display = 'none';
    logoutButton.style.display = 'block';
  }
  function handleLogout() {
    localStorage.removeItem('userInfo');
    loginButton.style.display = 'block';
    logoutButton.style.display = 'none';
    addMessage('You have been logged out.');
  }
  logoutButton.addEventListener('click', handleLogout);
  window.handleGoogleSignIn = handleGoogleSignIn;
  // Google Sign-In init
  window.onload = () => {
    google.accounts.id.initialize({
      client_id: '1077520511427-eh5nnii8tq4boml63jlftpc7bg2ihkqc.apps.googleusercontent.com',
      callback: handleGoogleSignIn,
      auto_select: false,
      cancel_on_tap_outside: true
    });
    // Check login status
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    if (userInfo) updateUIForLoggedInUser(userInfo);
  };

  // Update the initial greeting message
  document.querySelector('.bot-message .message-content').textContent = "Hello! I'm Tobi, your professional programming assistant. How can I help you today?";

  function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  }
  function updateUsageCounter() {
    if (isLoggedIn()) {
      usageCounter.style.display = 'none';
      return;
    }
    usageCounter.style.display = 'block';
    const used = getUsage();
    const left = Math.max(0, USAGE_LIMIT_SECONDS - used);
    usageCounter.textContent = `Usage: ${formatTime(used)} used / ${formatTime(left)} left today`;
  }
  // Update counter on load and on usage
  updateUsageCounter();
  // Update every second while input is focused
  let usageInterval = null;
  userInput.addEventListener('focus', () => {
    startUsageTimer();
    if (!usageInterval) usageInterval = setInterval(() => {
      if (!isLoggedIn()) updateUsageCounter();
    }, 1000);
  });
  userInput.addEventListener('blur', () => {
    stopUsageTimer();
    if (usageInterval) { clearInterval(usageInterval); usageInterval = null; }
    updateUsageCounter();
  });
  // Update on send and login/logout
  sendButton.addEventListener('click', updateUsageCounter);
  logoutButton.addEventListener('click', updateUsageCounter);
  loginButton.addEventListener('click', () => setTimeout(updateUsageCounter, 1000));
}); 