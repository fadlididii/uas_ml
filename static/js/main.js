document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const heroCreateAccountBtn = document.getElementById('heroCreateAccountBtn');
    const ctaGetStartedBtn = document.getElementById('ctaGetStartedBtn');
    const navGetStartedBtn = document.getElementById('navGetStartedBtn');
    const loginSubmitBtn = document.getElementById('loginSubmitBtn');
    const loginModal = document.getElementById('loginModal');
    const closeModalBtn = document.getElementById('closeModal');
    const closeLoginModal = document.getElementById('closeLoginModal');
    const passwordToggle = document.querySelector('.password-toggle');
    const passwordInput = document.getElementById('password');
    const loginForm = document.querySelector('.login-form') || document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showLoginModalLink = document.getElementById('showLoginModal');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // API Base URL
    const API_BASE = '/api';

    // Form validation functions
    function showError(input, message) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('error');
        formGroup.classList.remove('success');
        
        let errorElement = formGroup.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            formGroup.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    function showSuccess(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('success');
        formGroup.classList.remove('error');
        
        const errorElement = formGroup.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }

    function clearValidation(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.remove('error', 'success');
        
        const errorElement = formGroup.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }

    function validatePasswordMatch() {
        const password = passwordInput ? passwordInput.value : '';
        const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : '';
        
        if (confirmPassword && password !== confirmPassword) {
            showError(confirmPasswordInput, 'Passwords do not match');
        } else if (confirmPassword) {
            showSuccess(confirmPasswordInput);
        }
    }

    function validateField(e) {
        const input = e.target;
        const value = input.value.trim();
        
        // Clear previous validation
        clearValidation(input);
        
        // Skip validation if field is empty (required validation will handle it)
        if (!value && !input.hasAttribute('required')) return;
        
        switch (input.type) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (value && !emailRegex.test(value)) {
                    showError(input, 'Please enter a valid email address');
                } else if (value) {
                    showSuccess(input);
                }
                break;
                
            case 'password':
                if (input.id === 'password' || input.id === 'login_password') {
                    if (value.length < 6) {
                        showError(input, 'Password must be at least 6 characters long');
                    } else {
                        showSuccess(input);
                        // Also validate confirm password if it has value
                        if (confirmPasswordInput && confirmPasswordInput.value) {
                            validatePasswordMatch();
                        }
                    }
                } else if (input.id === 'confirm_password') {
                    validatePasswordMatch();
                }
                break;
                
            case 'text':
                if (input.hasAttribute('required') && value.length < 2) {
                    showError(input, 'This field must be at least 2 characters long');
                } else if (value) {
                    showSuccess(input);
                }
                break;
        }
    }

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

    function setLoading(form, isLoading) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const inputs = form.querySelectorAll('input, select');
        
        if (isLoading) {
            submitBtn.disabled = true;
            if (!submitBtn.dataset.originalText) {
                submitBtn.dataset.originalText = submitBtn.textContent;
            }
            submitBtn.textContent = 'Loading...';
            form.classList.add('loading');
            inputs.forEach(input => input.disabled = true);
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.originalText || (form.id === 'registerForm' ? 'Create Account' : 'Login');
            form.classList.remove('loading');
            
            // Ensure all inputs are enabled and interactive
            inputs.forEach(input => {
                input.disabled = false;
                input.style.pointerEvents = 'auto';
                input.style.backgroundColor = input.tagName === 'SELECT' ? 'white' : 'white';
            });
        }
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
            
            // Validate all fields
            let isValid = true;
            const formInputs = registerForm.querySelectorAll('input, select');
            
            formInputs.forEach(input => {
                if (input.hasAttribute('required') && !input.value.trim()) {
                    showError(input, 'This field is required');
                    isValid = false;
                } else {
                    validateField({ target: input });
                    if (input.closest('.form-group').classList.contains('error')) {
                        isValid = false;
                    }
                }
            });

            // Check password match
            if (passwordInput && confirmPasswordInput && passwordInput.value !== confirmPasswordInput.value) {
                showError(confirmPasswordInput, 'Passwords do not match');
                isValid = false;
            }

            console.log('Form validation result:', isValid);

            if (isValid) {
                // Show loading state
                const submitBtn = registerForm.querySelector('.btn-primary');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.textContent = 'Creating Account...';
                    submitBtn.disabled = true;
                }
                
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
                        submitBtn.textContent = 'Create Account';
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
                        submitBtn.textContent = 'Create Account';
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
                        
                        // Show field-specific errors
                        if (errorMessage.toLowerCase().includes('email')) {
                            showError(document.getElementById('email'), errorMessage);
                            return;
                        } else if (errorMessage.toLowerCase().includes('password')) {
                            showError(document.getElementById('password'), errorMessage);
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
            
            setLoading(this, true);
            
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
                setLoading(this, false);
            }
        });
    }

    // Real-time validation for all input fields
    const allInputs = document.querySelectorAll('input');
    allInputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateField({ target: input });
            }
        });
    });

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
        if (btn.textContent.trim() === 'Get Started') {
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