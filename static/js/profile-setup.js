// Profile Setup JavaScript

// Global variables for form validation

// Initialize the form
document.addEventListener('DOMContentLoaded', function() {
    // Setup event listeners
    setupEventListeners();
    
    console.log('Profile setup form initialized');
});


function validateForm() {
    console.log('Starting form validation...');
    
    const firstName = document.getElementById('firstName');
    const lastName = document.getElementById('lastName');
    const dateOfBirth = document.getElementById('dateOfBirth');
    const gender = document.getElementById('gender');
    const height = document.getElementById('height');
    const weight = document.getElementById('weight');
    const profilePhoto = document.getElementById('profilePhoto');
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(el => el.style.display = 'none');
    
    // Required fields validation
    if (!firstName || !firstName.value.trim()) {
        console.log('First name validation failed');
        if (firstName) showFieldError(firstName, 'First name is required');
        isValid = false;
    }
    
    if (!lastName || !lastName.value.trim()) {
        console.log('Last name validation failed');
        if (lastName) showFieldError(lastName, 'Last name is required');
        isValid = false;
    }
    
    if (!dateOfBirth || !dateOfBirth.value) {
        console.log('Date of birth validation failed');
        if (dateOfBirth) showFieldError(dateOfBirth, 'Date of birth is required');
        isValid = false;
    }
    
    if (!gender || !gender.value) {
        console.log('Gender validation failed');
        if (gender) showFieldError(gender, 'Gender is required');
        isValid = false;
    }
    
    // Optional fields validation (only if they have values)
    if (height && height.value && !validateHeight()) {
        console.log('Height validation failed');
        isValid = false;
    }
    
    if (weight && weight.value && !validateWeight()) {
        console.log('Weight validation failed');
        isValid = false;
    }
    
    // If profile photo is uploaded, validate it
    if (profilePhoto && profilePhoto.files.length > 0 && !validatePhotoFile(profilePhoto.files[0])) {
        console.log('Photo validation failed');
        isValid = false;
    }
    
    console.log('Form validation result:', isValid);
    return isValid;
}
    
function setupEventListeners() {
    // Form submission
    const form = document.getElementById('profileSetupForm');
    if (form) {
        form.addEventListener('submit', handleSubmit);
        console.log('Form submit event listener attached');
    } else {
        console.error('Form with ID profileSetupForm not found');
    }
    
    // Social care slider
    const socialCareSlider = document.getElementById('socialCare');
    if (socialCareSlider) {
        socialCareSlider.addEventListener('input', updateSocialCareValue);
        // Initialize value display
        updateSocialCareValue();
    }
    
    // Photo upload handling
    const photoInput = document.getElementById('profilePhoto');
    if (photoInput) {
        photoInput.addEventListener('change', handlePhotoUpload);
    }
    
    // Remove photo button
    const removePhotoBtn = document.getElementById('removePhoto');
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener('click', removePhoto);
    }
    
    // Photo URL preview
    const photoUrlInput = document.getElementById('photoUrl');
    if (photoUrlInput) {
        photoUrlInput.addEventListener('blur', previewPhoto);
    }
    
    // Clear validation errors when inputs change
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            clearFieldError(input);
        });
    });
    
    // Clear radio group errors when any radio is selected
    const radioGroups = document.querySelectorAll('.radio-group');
    radioGroups.forEach(group => {
        const radios = group.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', () => {
                const errorDiv = group.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            });
        });
    });
}
    
function setupValidation() {
    // Real-time validation for required fields
    const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearFieldError(input));
    });
    
    // Age validation
    const birthDateInput = document.getElementById('dateOfBirth');
    if (birthDateInput) {
        birthDateInput.addEventListener('change', validateAge);
    }
    
    // Height and weight validation
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    if (heightInput) {
        heightInput.addEventListener('input', validateHeight);
    }
    if (weightInput) {
        weightInput.addEventListener('input', validateWeight);
    }
    
    // Photo URL validation
    const photoUrlInput = document.getElementById('photoUrl');
    if (photoUrlInput) {
        photoUrlInput.addEventListener('input', validatePhotoUrl);
    }
}
    
function validateStep1() {
    const firstName = document.getElementById('firstName');
    const lastName = document.getElementById('lastName');
    const dateOfBirth = document.getElementById('dateOfBirth');
    const gender = document.getElementById('gender');
    
    let isValid = true;
    
    if (!firstName.value.trim()) {
        showFieldError(firstName, 'First name is required');
        isValid = false;
    }
    
    if (!lastName.value.trim()) {
        showFieldError(lastName, 'Last name is required');
        isValid = false;
    }
    
    if (!dateOfBirth.value) {
        showFieldError(dateOfBirth, 'Date of birth is required');
        isValid = false;
    } else if (!validateAge()) {
        isValid = false;
    }
    
    if (!gender.value) {
        showFieldError(gender, 'Gender is required');
        isValid = false;
    }
    
    return isValid;
}

function validateStep2() {
    const height = document.getElementById('height');
    const weight = document.getElementById('weight');
    
    let isValid = true;
    
    if (height.value && !validateHeight()) {
        isValid = false;
    }
    
    if (weight.value && !validateWeight()) {
        isValid = false;
    }
    
    return isValid;
}

function validateAge() {
    const birthDateInput = document.getElementById('dateOfBirth');
    if (!birthDateInput || !birthDateInput.value) return false;
    
    const birthDate = new Date(birthDateInput.value);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    const isValid = age >= 18;
    
    if (!isValid) {
        showFieldError(birthDateInput, 'You must be at least 18 years old');
    } else {
        clearFieldError(birthDateInput);
    }
    
    return isValid;
}

function validateHeight() {
    const heightInput = document.getElementById('height');
    if (!heightInput) return true;
    
    const height = parseInt(heightInput.value);
    const isValid = height >= 100 && height <= 250;
    
    if (!isValid && heightInput.value) {
        showFieldError(heightInput, 'Height must be between 100-250 cm');
    } else {
        clearFieldError(heightInput);
    }
    
    return isValid;
}

function validateWeight() {
    const weightInput = document.getElementById('weight');
    if (!weightInput) return true;
    
    const weight = parseInt(weightInput.value);
    const isValid = weight >= 30 && weight <= 300;
    
    if (!isValid && weightInput.value) {
        showFieldError(weightInput, 'Weight must be between 30-300 kg');
    } else {
        clearFieldError(weightInput);
    }
    
    return isValid;
}

function validatePhotoUrl() {
    const photoUrlInput = document.getElementById('photoUrl');
    if (!photoUrlInput) return true;
    
    const url = photoUrlInput.value.trim();
    
    if (!url) return true; // Optional field
    
    const urlPattern = /^https?:\/\/.+\.(jpg|jpeg|png|gif|webp)(\?.*)?$/i;
    const isValid = urlPattern.test(url);
    
    if (!isValid) {
        showFieldError(photoUrlInput, 'Please enter a valid image URL (jpg, png, gif, webp)');
    } else {
        clearFieldError(photoUrlInput);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function updateSocialCareValue() {
    const slider = document.getElementById('socialCare');
    if (slider) {
        const value = slider.value;
        const labels = slider.parentNode.querySelector('.range-labels');
        if (labels) {
            labels.innerHTML = `<span>Low (${value})</span><span>High</span>`;
        }
        
        // Also update value display if it exists
        const valueDisplay = document.getElementById('socialCareValue');
        if (valueDisplay) {
            valueDisplay.textContent = value;
        }
    }
}

function handlePhotoUpload(event) {
    const file = event.target.files[0];
    
    if (!file) {
        hidePhotoPreview();
        return;
    }
    
    // Validate file
    if (!validatePhotoFile(file)) {
        event.target.value = ''; // Clear the input
        hidePhotoPreview();
        return;
    }
    
    // Show preview
    showPhotoPreview(file);
}

function validatePhotoFile(file) {
    const photoInput = document.getElementById('profilePhoto');
    
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showFieldError(photoInput, 'Please select a valid image file (JPG, PNG, GIF, WebP)');
        return false;
    }
    
    // Check file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showFieldError(photoInput, 'File size must be less than 5MB');
        return false;
    }
    
    clearFieldError(photoInput);
    return true;
}

function showPhotoPreview(file) {
    const previewContainer = document.getElementById('photoPreview');
    const previewImage = document.getElementById('previewImage');
    
    if (!previewContainer || !previewImage) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function hidePhotoPreview() {
    const previewContainer = document.getElementById('photoPreview');
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
}

function removePhoto() {
    const photoInput = document.getElementById('profilePhoto');
    if (photoInput) {
        photoInput.value = '';
        clearFieldError(photoInput);
    }
    hidePhotoPreview();
}

function previewPhoto() {
    const photoUrlInput = document.getElementById('photoUrl');
    const previewContainer = document.getElementById('photoPreview');
    
    if (!photoUrlInput || !previewContainer) return;
    
    const url = photoUrlInput.value.trim();
    
    if (url && validatePhotoUrl()) {
        previewContainer.innerHTML = `<img src="${url}" alt="Profile Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">`;
    } else {
        previewContainer.innerHTML = '';
    }
}
    
function handleSubmit(e) {
    console.log('Form submit triggered');
    e.preventDefault();
    
    // Validate all fields
    if (!validateForm()) {
        console.log('Form validation failed');
        return;
    }
    
    console.log('Form validation passed, submitting...');

    
    // Show loading state
    showLoading(true);
    
    // Collect form data
    const formData = collectFormData();
    
    // Submit to API (using FormData for file upload support)
    fetch('/api/profile', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error submitting profile:', error);
        showError('Network error. Please try again.');
    })
    .finally(() => {
        showLoading(false);
    });
}

function collectFormData() {
    const form = document.getElementById('profileSetupForm');
    const formData = new FormData(form);
    
    // Map form field names to API field names
    formData.set('first_name', formData.get('firstName'));
    formData.delete('firstName');
    
    formData.set('last_name', formData.get('lastName'));
    formData.delete('lastName');
    
    formData.set('date_of_birth', formData.get('dateOfBirth'));
    formData.delete('dateOfBirth');
    
    // Convert specific fields to appropriate types
    const heightValue = formData.get('height');
    if (heightValue) formData.set('height', parseInt(heightValue));
    
    const weightValue = formData.get('weight');
    if (weightValue) formData.set('weight', parseInt(weightValue));
    
    const socialCareValue = formData.get('socialCare');
    if (socialCareValue) {
        formData.set('social_care', parseInt(socialCareValue));
        formData.delete('socialCare');
    }
    
    // Convert boolean fields
    const smokingValue = formData.get('smoking');
    if (smokingValue !== null) {
        formData.set('smoking', smokingValue === 'yes');
        formData.delete('smoking');
    }
    
    // Handle pets field
    const petsValue = formData.get('pets');
    if (petsValue !== null) {
        formData.set('have_pets', petsValue === 'yes');
        formData.delete('pets');
    }
    
    // Set bio field
    const bioValue = formData.get('bio');
    if (bioValue) formData.set('bio', bioValue);
    
    return formData;
}

function showError(message) {
    // Create or update error alert
    let errorAlert = document.getElementById('errorAlert');
    if (!errorAlert) {
        errorAlert = document.createElement('div');
        errorAlert.id = 'errorAlert';
        errorAlert.className = 'alert alert-danger alert-dismissible fade show';
        
        const form = document.getElementById('profileSetupForm');
        form.insertBefore(errorAlert, form.firstChild);
    }
    
    errorAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorAlert) {
            errorAlert.remove();
        }
    }, 5000);
}

function showLoading(show) {
    let loadingModal = document.getElementById('loadingModal');
    
    // Create loading modal if it doesn't exist
    if (!loadingModal) {
        loadingModal = document.createElement('div');
        loadingModal.id = 'loadingModal';
        loadingModal.className = 'loading-modal';
        loadingModal.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Saving your profile...</p>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .loading-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            .loading-content {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .loading-content p {
                margin-top: 15px;
                font-weight: 500;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(loadingModal);
    }
    
    if (show) {
        loadingModal.style.display = 'flex';
    } else {
        loadingModal.style.display = 'none';
    }
}