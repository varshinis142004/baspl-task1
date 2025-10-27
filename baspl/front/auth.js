// keep toggle behavior
const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', () => container.classList.add('active'));
loginBtn.addEventListener('click', () => container.classList.remove('active'));

// Helper: show messages
function showMessage(el, text, isError = true) {
  if (!el) return;
  el.style.display = 'block';
  el.style.color = isError ? '#b91c1c' : '#0b6623';
  el.textContent = text;
}
function hideMessage(el) { if (el) el.style.display = 'none'; }

// Basic client-side validators
function isValidEmail(email) {
  return /[^@]+@[^@]+\.[^@]+/.test(email);
}

// Login handling
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideMessage(loginError);

  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;

  if (!username || !password) {
    showMessage(loginError, 'Please enter both username and password.');
    return;
  }

  try {
    const resp = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const result = await resp.json();

    if (resp.ok && result.success) {
      // Redirect to dashboard (served by Flask)
      window.location.href = '/dashboard.html';
    } else {
      // show server-provided message
      showMessage(loginError, result.error || 'Login failed. Please try again.');
    }
  } catch (err) {
    console.error(err);
    showMessage(loginError, 'Server unreachable. Make sure the backend is running.');
  }
});

// Signup handling
const signupForm = document.getElementById('signupForm');
const signupError = document.getElementById('signupError');
const signupSuccess = document.getElementById('signupSuccess');

signupForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideMessage(signupError);
  hideMessage(signupSuccess);

  const username = document.getElementById('signupUsername').value.trim();
  const email = document.getElementById('signupEmail').value.trim();
  const password = document.getElementById('signupPassword').value;

  if (!username || !email || !password) {
    showMessage(signupError, 'All fields are required.');
    return;
  }
  if (!isValidEmail(email)) {
    showMessage(signupError, 'Enter a valid email address.');
    return;
  }
  if (password.length < 6) {
    showMessage(signupError, 'Password must be at least 6 characters.');
    return;
  }

  try {
    const resp = await fetch('/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });

    const result = await resp.json();

    if (resp.ok && result.success) {
      showMessage(signupSuccess, 'Registered successfully — you can now login.', false);
      // Optionally switch to login panel automatically
      setTimeout(() => {
        container.classList.remove('active');
      }, 800);
    } else {
      showMessage(signupError, result.error || 'Registration failed. Try another username.');
    }
  } catch (err) {
    console.error(err);
    showMessage(signupError, 'Server unreachable. Make sure the backend is running.');
  }
});
