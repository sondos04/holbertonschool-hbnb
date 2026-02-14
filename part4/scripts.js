// ============================================
// HBnB - Final Clean JavaScript
// ============================================

const API_URL = 'http://127.0.0.1:5000/api/v1';

// ========== Cookie Helpers ==========
function getCookie(name) {
    const value = ; ${document.cookie};
    const parts = value.split(; ${name}=);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days = 7) {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = ${name}=${value}; path=/; expires=${d.toUTCString()};
}

function deleteCookie(name) {
    document.cookie = ${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;
}

// ========== Auth Functions ==========
function isAuthenticated() {
    return getCookie('token') !== null;
}

function updateAuthUI() {
    const loginBtn = document.getElementById('login-btn');
    const userMenu = document.getElementById('user-menu');
    const userInitial = document.getElementById('user-initial');
    const email = localStorage.getItem('userEmail');

    if (isAuthenticated() && email) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (userMenu) {
            userMenu.classList.remove('hidden');
            userMenu.classList.add('flex');
        }
        if (userInitial) {
            userInitial.textContent = email.charAt(0).toUpperCase();
        }
    } else {
        if (loginBtn) loginBtn.style.display = 'inline-block';
        if (userMenu) {
            userMenu.classList.add('hidden');
            userMenu.classList.remove('flex');
        }
    }
}
