/**
 * Here Ye Health - Medieval Theme JavaScript
 */

// Dom Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    // Language selection buttons
    const languageButtons = document.querySelectorAll('.language-scroll-button');
    if (languageButtons.length > 0) {
        languageButtons.forEach(button => {
            button.addEventListener('click', function() {
                const lang = this.getAttribute('data-lang');
                document.getElementById('selectedLanguage').value = lang;
                showLoadingScreen();
                document.getElementById('languageForm').submit();
            });
        });
    }
    
    // Back buttons
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.history.back();
        });
    }
    
    const languageBackButton = document.getElementById('language-back-button');
    if (languageBackButton) {
        languageBackButton.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
    
    // Hide loading screen if it's visible when the page loads
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen && loadingScreen.style.display === 'flex') {
        loadingScreen.style.display = 'none';
    }
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Validate input
            if (!username || !password) {
                alert('Pray provide both thy scroll number and secret word!');
                return;
            }
            
            showLoadingScreen();
            
            // Submit the form to the server
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Login failed');
                }
                return response.json();
            })
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    hideLoadingScreen();
                    alert('The royal archivist could not find thy records. Try again.');
                }
            })
            .catch(error => {
                hideLoadingScreen();
                alert('A magical error occurred while accessing the royal archives.');
                console.error('Error:', error);
            });
        });
    }
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    if (phoneInputs.length > 0) {
        phoneInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                const input = e.target;
                let value = input.value.replace(/\D/g, '');
                
                if (value.length > 0 && !value.startsWith('+')) {
                    value = '+' + value;
                }
                
                input.value = value;
            });
        });
    }
});

/**
 * Show the medieval loading screen with hourglass animation
 */
function showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'flex';
    }
}

/**
 * Hide the medieval loading screen
 */
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
    }
}

/**
 * Validate phone number in medieval style
 */
function validatePhoneNumber() {
    const phoneNumber = document.getElementById('to_number').value;
    const regex = /^\+?\d{10,15}$/;
    
    if (!regex.test(phoneNumber)) {
        alert("Alas! Thy scroll number appears to be incorrectly inscribed. Please use the proper format beginning with a '+' followed by digits.");
        return false;
    }
    
    return true;
}

