document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('errorMsg');

    errorMsg.style.display = 'none';
    errorMsg.textContent   = '';

    if (!email || !password) {
        showError('Please enter email and password');
        return;
    }

    const submitBtn   = e.target.querySelector('button');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Signing In...`;

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username:  email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Save tokens and user info
            localStorage.setItem('accessToken',  data.access_token);
            localStorage.setItem('user',         JSON.stringify(data.user));

            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            const msg = data.detail || 'Invalid email or password';
            showError(msg);
        }

    } catch (err) {
        console.error(err);
        showError('Cannot connect to server. Is the backend running?');
    } finally {
        submitBtn.disabled  = false;
        submitBtn.innerHTML = originalText;
    }
});

function showError(message) {
    const errorMsg = document.getElementById('errorMsg');
    errorMsg.textContent    = message;
    errorMsg.style.display  = 'block';
}