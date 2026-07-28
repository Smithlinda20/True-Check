// ==================== MOBILE MENU TOGGLE ====================
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');

    if (navbarToggle) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });

        // Close menu when clicking on a link
        const navLinks = navbarMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarMenu.classList.remove('active');
            });
        });
    }

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (navbarMenu && !navbarMenu.contains(event.target) && !navbarToggle.contains(event.target)) {
            navbarMenu.classList.remove('active');
        }
    });

    // ==================== AUTO-CLOSE ALERTS ====================
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }

        // Auto-close success alerts after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });

    // ==================== FORM VALIDATION ====================
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#E74C3C';
                    
                    // Show error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('form-error')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.style.borderColor = '';
                    
                    // Remove error message
                    let errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('form-error')) {
                        errorMsg.remove();
                    }
                }
            });

            // Email validation
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (field.value && !emailRegex.test(field.value)) {
                    isValid = false;
                    field.style.borderColor = '#E74C3C';
                    
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('form-error')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.textContent = 'Please enter a valid email address';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Clear error on field focus
        const allFields = form.querySelectorAll('input, textarea, select');
        allFields.forEach(field => {
            field.addEventListener('focus', function() {
                this.style.borderColor = '';
                const errorMsg = this.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('form-error')) {
                    errorMsg.remove();
                }
            });
        });
    });

    // ==================== PASSWORD STRENGTH INDICATOR ====================
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;

            // Display strength indicator if exists
            const indicator = this.nextElementSibling;
            if (indicator && indicator.classList.contains('password-strength')) {
                let strengthText = '';
                let strengthColor = '';

                if (strength === 0) {
                    strengthText = '';
                    strengthColor = '#999';
                } else if (strength === 1) {
                    strengthText = 'Weak';
                    strengthColor = '#E74C3C';
                } else if (strength === 2) {
                    strengthText = 'Fair';
                    strengthColor = '#F39C12';
                } else if (strength === 3) {
                    strengthText = 'Good';
                    strengthColor = '#3498DB';
                } else if (strength === 4) {
                    strengthText = 'Strong';
                    strengthColor = '#27AE60';
                }

                indicator.textContent = strengthText;
                indicator.style.color = strengthColor;
            }
        });
    });

    // ==================== CONFIRM PASSWORD VALIDATION ====================
    const passwordConfirmInputs = document.querySelectorAll('input[name="password_confirm"]');
    passwordConfirmInputs.forEach(confirmInput => {
        confirmInput.addEventListener('input', function() {
            const passwordInput = document.querySelector('input[name="password"]');
            if (passwordInput) {
                if (this.value !== passwordInput.value && this.value.length > 0) {
                    this.style.borderColor = '#E74C3C';
                    
                    let errorMsg = this.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('form-error')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.textContent = 'Passwords do not match';
                        this.parentNode.insertBefore(errorMsg, this.nextSibling);
                    }
                } else {
                    this.style.borderColor = '';
                    let errorMsg = this.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('form-error')) {
                        errorMsg.remove();
                    }
                }
            }
        });
    });

    // ==================== COPY TO CLIPBOARD ====================
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            });
        });
    });

    // ==================== SMOOTH SCROLL FOR ANCHOR LINKS ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // ==================== NUMBER FORMATTING ====================
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // ==================== FILE INPUT PREVIEW ====================
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                const fileName = files[0].name;
                const fileSize = (files[0].size / 1024).toFixed(2) + ' KB';
                
                // Display file info if element exists
                let fileInfo = this.nextElementSibling;
                if (!fileInfo || !fileInfo.classList.contains('file-info')) {
                    fileInfo = document.createElement('div');
                    fileInfo.className = 'file-info';
                    this.parentNode.insertBefore(fileInfo, this.nextSibling);
                }
                fileInfo.textContent = `Selected: ${fileName} (${fileSize})`;
                fileInfo.style.color = '#27AE60';
                fileInfo.style.marginTop = '8px';
                fileInfo.style.fontSize = '0.9rem';
            }
        });
    });

    // ==================== MODAL HANDLING ====================
    const closeButtons = document.querySelectorAll('[data-close-modal]');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    modal.style.display = 'none';
                }, 300);
            }
        });
    });

    // ==================== LOADING STATE ====================
    const forms2 = document.querySelectorAll('form');
    forms2.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            form.addEventListener('submit', function() {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
            });
        }
    });

    // ==================== NOTIFICATION DISMISS ====================
    document.querySelectorAll('[data-notification-dismiss]').forEach(elem => {
        elem.addEventListener('click', function() {
            const notificationId = this.getAttribute('data-notification-dismiss');
            fetch(`/notification/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            }).then(response => {
                if (response.ok) {
                    this.closest('.notification-item').style.opacity = '0.5';
                }
            });
        });
    });
});

// ==================== UTILITY FUNCTIONS ====================

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="alert-close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.messages-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    if (duration > 0) {
        setTimeout(() => {
            alertDiv.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => {
                alertDiv.remove();
            }, 300);
        }, duration);
    }
}

// Add CSS animation for slideUp
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
    @keyframes fadeOut {
        to {
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);