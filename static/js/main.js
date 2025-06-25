document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const heroCreateAccountBtn = document.getElementById('heroCreateAccountBtn');
    const ctaGetStartedBtn = document.getElementById('ctaGetStartedBtn');
    const navGetStartedBtn = document.getElementById('navGetStartedBtn');
    const loginModal = document.getElementById('loginModal');
    const closeModalBtn = document.getElementById('closeModal');
    const closeLoginModal = document.getElementById('closeLoginModal');
    const passwordInput = document.getElementById('password');
    const loginForm = document.querySelector('.login-form') || document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showLoginModalLink = document.getElementById('showLoginModal');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // API Base URL
    const API_BASE = '/api';

    // Utility functions

    // Utility functions
    function showMessage(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;
        
        // Add styles if not exist
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    z-index: 10000;
                    transform: translateX(400px);
                    transition: transform 0.3s ease;
                    max-width: 400px;
                }
                .toast.show { transform: translateX(0); }
                .toast-success { background: #10b981; }
                .toast-error { background: #ef4444; }
                .toast-info { background: #3b82f6; }
                .toast-content { display: flex; justify-content: space-between; align-items: center; }
                .toast-close { background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: 10px; }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
    }



    // Modal functions are implemented in register.html

    // Register form submission
    if (registerForm) {
        // Ensure button is clickable
        const submitBtn = registerForm.querySelector('.btn-primary');
        if (submitBtn) {
            submitBtn.style.pointerEvents = 'auto';
            submitBtn.disabled = false;
            console.log('Register button initialized and enabled');
        }
        
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Register form submitted');
            
            // Simple validation
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (!email || !password || !confirmPassword) {
                showMessage('Please fill in all fields', 'error');
                return;
            }
            
            if (password !== confirmPassword) {
                showMessage('Passwords do not match', 'error');
                return;
            }
            
            console.log('Form validation passed');
            {
                // Show loading state
                const submitBtn = registerForm.querySelector('.btn-primary');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.textContent = 'Creating Account...';
                    submitBtn.disabled = true;
                }
                
                // Disable all inputs
                const formInputs = registerForm.querySelectorAll('input, select');
                formInputs.forEach(input => input.disabled = true);
                
                // Prepare form data - only email and password for initial registration
                const formData = {
                    email: document.getElementById('email').value.trim(),
                    password: document.getElementById('password').value
                };
                
                console.log('Submitting registration data:', formData);
                
                // Submit to backend API
                fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => {
                    console.log('Registration response status:', response.status);
                    if (response.ok) {
                        return response.json();
                    } else {
                        return response.json().then(err => Promise.reject(err));
                    }
                })
                .then(data => {
                    console.log('Registration success:', data);
                    // Success response
                    if (submitBtn) {
                        submitBtn.classList.remove('loading');
                        submitBtn.textContent = 'Buat Akun';
                        submitBtn.disabled = false;
                    }
                    
                    // Show success message
                    showMessage(`Account created successfully! Please complete your profile.`, 'success');
                    
                    // Reset form
                    registerForm.reset();
                    
                    // Redirect to login page
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                })
                .catch(error => {
                    console.error('Registration error:', error);
                    // Error handling
                    if (submitBtn) {
                        submitBtn.classList.remove('loading');
                        submitBtn.textContent = 'Buat Akun';
                        submitBtn.disabled = false;
                    }
                    
                    let errorMessage = 'Registration failed. Please try again.';
                    
                    // Handle different error response formats
                    if (error && typeof error === 'object') {
                        if (error.error) {
                            // Flask API error format
                            errorMessage = error.error;
                        } else if (error.message) {
                            errorMessage = error.message;
                        } else if (error.detail) {
                            errorMessage = Array.isArray(error.detail) ? error.detail[0].msg : error.detail;
                        }
                        
                        // Show field-specific errors in toast message
                        if (errorMessage.toLowerCase().includes('email') || errorMessage.toLowerCase().includes('password')) {
                            showMessage(errorMessage, 'error');
                            return;
                        }
                    } else if (typeof error === 'string') {
                        errorMessage = error;
                    }
                    
                    showMessage(`Registration failed: ${errorMessage}`, 'error');
                });
            }
        });
    }

    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailField = document.getElementById('email') || document.getElementById('login_email');
            const passwordField = document.getElementById('password') || document.getElementById('login_password');
            
            const email = emailField ? emailField.value : '';
            const password = passwordField ? passwordField.value : '';
            
            if (!email || !password) {
                showMessage('Please fill in all fields', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
            }
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Store user data in localStorage
                    if (data.data) {
                        localStorage.setItem('user_data', JSON.stringify(data.data));
                        localStorage.setItem('user_id', data.data.user_id);
                    }
                    
                    showMessage('Login successful!', 'success');
                    
                    // Hide modal if exists
                    if (typeof hideLoginModal === 'function') {
                        hideLoginModal();
                    }
                    
                    // Check profile and preferences status and redirect accordingly
                    const userData = data.data || {};
                    if (userData.has_profile && userData.has_preferences) {
                        setTimeout(() => {
                            window.location.href = '/match-feed';
                        }, 1000);
                    } else if (userData.has_profile) {
                        setTimeout(() => {
                            window.location.href = '/preferences';
                        }, 1000);
                    } else {
                        setTimeout(() => {
                            window.location.href = '/profile-setup';
                        }, 1000);
                    }
                } else {
                    let errorMessage = 'Login failed';
                    if (data.error) {
                        errorMessage = data.error;
                    } else if (data.message) {
                        errorMessage = data.message;
                    }
                    showMessage(errorMessage, 'error');
                }
            } catch (error) {
                console.error('Login error:', error);
                showMessage('Network error. Please try again.', 'error');
            } finally {
                // Reset loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Login';
                }
            }
        });
    }



    // Ensure form fields are interactive on page load
    if (registerForm) {
        const inputs = registerForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.disabled = false;
            input.style.pointerEvents = 'auto';
            input.style.backgroundColor = 'white';
            input.style.cursor = input.tagName === 'SELECT' ? 'pointer' : 'text';
        });
        
        // Additional button click handler as backup
        const submitBtn = registerForm.querySelector('.btn-primary');
        if (submitBtn) {
            submitBtn.addEventListener('click', function(e) {
                console.log('Button clicked directly');
                // Let the form submit event handle the logic
                if (e.target.type !== 'submit') {
                    e.preventDefault();
                    registerForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            });
        }
    }

    // Modal event listeners (functions defined at the end)

    // Show login modal link
    if (showLoginModalLink) {
        showLoginModalLink.addEventListener('click', (e) => {
            e.preventDefault();
            showLoginModal();
        });
    }

    // Event listeners for buttons that should show login modal
    if (heroCreateAccountBtn) {
        heroCreateAccountBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showLoginModal();
        });
    }

    if (ctaGetStartedBtn) {
        ctaGetStartedBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showLoginModal();
        });
    }

    if (navGetStartedBtn) {
        navGetStartedBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showLoginModal();
        });
    }

    // Get Started button in navbar (without ID)
    const navGetStartedBtns = document.querySelectorAll('.nav-links .btn-primary');
    navGetStartedBtns.forEach(btn => {
        if (btn.textContent.trim() === 'Mulai') {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                showLoginModal();
            });
        }
    });

    // Close modal event listeners
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', hideLoginModal);
    }

    if (closeLoginModal) {
        closeLoginModal.addEventListener('click', (e) => {
            e.preventDefault();
            hideLoginModal();
        });
    }

    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                hideLoginModal();
            }
        });
    }

    // Password show/hide toggle functionality for all password toggles
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const input = e.target.previousElementSibling;
            if (input && input.type) {
                if (input.type === 'password') {
                    input.type = 'text';
                    e.target.textContent = '🙈';
                } else {
                    input.type = 'password';
                    e.target.textContent = '👁️';
                }
            }
        });
    });

    // Enhanced modal show/hide with animation
    function showLoginModal() {
        if (loginModal) {
            loginModal.style.display = 'flex';
            loginModal.classList.remove('hidden');
            // Reset form if exists
            const form = loginModal.querySelector('form');
            if (form) {
                form.reset();
                // Clear any validation messages
                const errorMessages = form.querySelectorAll('.error-message');
                errorMessages.forEach(msg => msg.remove());
                const formGroups = form.querySelectorAll('.form-group');
                formGroups.forEach(group => group.classList.remove('error', 'success'));
            }
            setTimeout(() => {
                loginModal.classList.add('show');
            }, 10);
        }
    }

    function hideLoginModal() {
        if (loginModal) {
            loginModal.classList.remove('show');
            setTimeout(() => {
                loginModal.classList.add('hidden');
                loginModal.style.display = 'none';
            }, 300);
        }
    }

    // Make functions globally available
    window.showLoginModal = showLoginModal;
    window.hideLoginModal = hideLoginModal;
});


// Mobile menu functionality
const hamburgerMenu = document.getElementById('hamburgerMenu');
const navLinks = document.getElementById('navLinks');

if (hamburgerMenu && navLinks) {
    hamburgerMenu.addEventListener('click', function() {
        hamburgerMenu.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking on a link
    const navLinksItems = navLinks.querySelectorAll('a');
    navLinksItems.forEach(link => {
        link.addEventListener('click', function() {
            hamburgerMenu.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!navLinks.contains(event.target) && !hamburgerMenu.contains(event.target) && navLinks.classList.contains('active')) {
            hamburgerMenu.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
}