// Profile Setup JavaScript

// Global variables for form validation

// Initialize the form
document.addEventListener('DOMContentLoaded', function() {
    // Setup event listeners
    setupEventListeners();
    
    // Setup validation
    setupValidation();
    
    console.log('Profile setup form initialized');
});


function validateForm() {
    console.log('Starting form validation...');
    
    const firstName = document.getElementById('firstName');
    const lastName = document.getElementById('lastName');
    const dateOfBirth = document.getElementById('dateOfBirth');
    const gender = document.getElementById('gender');
    const height = document.getElementById('height_cm');
    const weight = document.getElementById('weight_kg');
    const profilePhoto = document.getElementById('profilePhoto');
    const religion = document.getElementById('religion');
    const provinsi = document.getElementById('provinsi');
    const kabupaten = document.getElementById('kabupaten');
    const relationshipGoal = document.querySelector('input[name="relationship_goal"]:checked');
    
    let isValid = true;
    let firstErrorElement = null;
    
    // Clear previous errors
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(el => el.style.display = 'none');
    
    // Required fields validation
    if (!firstName || !firstName.value.trim()) {
        console.log('First name validation failed');
        if (firstName) {
            showFieldError(firstName, 'Nama depan wajib diisi');
            if (!firstErrorElement) firstErrorElement = firstName;
        }
        isValid = false;
    }
    
    if (!lastName || !lastName.value.trim()) {
        console.log('Last name validation failed');
        if (lastName) {
            showFieldError(lastName, 'Nama belakang wajib diisi');
            if (!firstErrorElement) firstErrorElement = lastName;
        }
        isValid = false;
    }
    
    if (!dateOfBirth || !dateOfBirth.value) {
        console.log('Date of birth validation failed');
        if (dateOfBirth) {
            showFieldError(dateOfBirth, 'Tanggal lahir wajib diisi');
            if (!firstErrorElement) firstErrorElement = dateOfBirth;
        }
        isValid = false;
    } else if (!validateAge()) {
        console.log('Age validation failed');
        if (!firstErrorElement) firstErrorElement = dateOfBirth;
        isValid = false;
    }
    
    if (!gender || !gender.value) {
        console.log('Gender validation failed');
        if (gender) {
            showFieldError(gender, 'Jenis kelamin wajib dipilih');
            if (!firstErrorElement) firstErrorElement = gender;
        }
        isValid = false;
    }
    
    if (!religion || !religion.value) {
        console.log('Religion validation failed');
        if (religion) {
            showFieldError(religion, 'Agama wajib dipilih');
            if (!firstErrorElement) firstErrorElement = religion;
        }
        isValid = false;
    }
    
    if (!provinsi || !provinsi.value) {
        console.log('Provinsi validation failed');
        if (provinsi) {
            showFieldError(provinsi, 'Provinsi wajib dipilih');
            if (!firstErrorElement) firstErrorElement = provinsi;
        }
        isValid = false;
    }
    
    if (!kabupaten || !kabupaten.value) {
        console.log('Kabupaten validation failed');
        if (kabupaten) {
            showFieldError(kabupaten, 'Kabupaten/Kota wajib dipilih');
            if (!firstErrorElement) firstErrorElement = kabupaten;
        }
        isValid = false;
    }
    
    if (!relationshipGoal) {
        console.log('Relationship goal validation failed');
        const relationshipInput = document.querySelector('input[name="relationship_goal"]');
        if (relationshipInput) {
            const container = relationshipInput.closest('.radio-group');
            if (container) {
                container.classList.add('is-invalid');
                let errorDiv = container.querySelector('.invalid-feedback');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    container.appendChild(errorDiv);
                }
                errorDiv.textContent = 'Tujuan hubungan wajib dipilih';
                errorDiv.style.display = 'block';
                if (!firstErrorElement) firstErrorElement = relationshipInput;
            }
        }
        isValid = false;
    }
    
    // Optional fields validation (only if they have values)
    if (height && height.value && !validateHeight()) {
        console.log('Height validation failed');
        if (!firstErrorElement) firstErrorElement = height;
        isValid = false;
    }
    
    if (weight && weight.value && !validateWeight()) {
        console.log('Weight validation failed');
        if (!firstErrorElement) firstErrorElement = weight;
        isValid = false;
    }
    
    // If profile photo is uploaded, validate it
    if (profilePhoto && profilePhoto.files.length > 0 && !validatePhotoFile(profilePhoto.files[0])) {
        console.log('Photo validation failed');
        if (!firstErrorElement) firstErrorElement = profilePhoto;
        isValid = false;
    }
    
    // Scroll to the first error element
    if (firstErrorElement && !isElementInViewport(firstErrorElement)) {
        setTimeout(() => {
            firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
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
        birthDateInput.addEventListener('blur', validateAge);
    }
    
    // Height and weight validation
    const heightInput = document.getElementById('height_cm');
    const weightInput = document.getElementById('weight_kg');
    if (heightInput) {
        heightInput.addEventListener('input', validateHeight);
        heightInput.addEventListener('blur', validateHeight);
    }
    if (weightInput) {
        weightInput.addEventListener('input', validateWeight);
        weightInput.addEventListener('blur', validateWeight);
    }
    
    // Photo URL validation
    const photoUrlInput = document.getElementById('photoUrl');
    if (photoUrlInput) {
        photoUrlInput.addEventListener('input', validatePhotoUrl);
    }
    
    // First name validation
    const firstNameInput = document.getElementById('firstName');
    if (firstNameInput) {
        firstNameInput.addEventListener('blur', () => validateRequired(firstNameInput, 'Nama depan wajib diisi'));
        firstNameInput.addEventListener('input', () => clearFieldError(firstNameInput));
    }
    
    // Last name validation
    const lastNameInput = document.getElementById('lastName');
    if (lastNameInput) {
        lastNameInput.addEventListener('blur', () => validateRequired(lastNameInput, 'Nama belakang wajib diisi'));
        lastNameInput.addEventListener('input', () => clearFieldError(lastNameInput));
    }
    
    // Gender validation
    const genderInput = document.getElementById('gender');
    if (genderInput) {
        genderInput.addEventListener('blur', () => validateRequired(genderInput, 'Jenis kelamin wajib dipilih'));
        genderInput.addEventListener('change', () => clearFieldError(genderInput));
    }
    
    // Religion validation
    const religionInput = document.getElementById('religion');
    if (religionInput) {
        religionInput.addEventListener('blur', () => validateRequired(religionInput, 'Agama wajib dipilih'));
        religionInput.addEventListener('change', () => clearFieldError(religionInput));
    }
    
    // Location validation
    const provinsiInput = document.getElementById('provinsi');
    const kabupatenInput = document.getElementById('kabupaten');
    if (provinsiInput) {
        provinsiInput.addEventListener('blur', () => validateRequired(provinsiInput, 'Provinsi wajib dipilih'));
        provinsiInput.addEventListener('change', () => {
            clearFieldError(provinsiInput);
            if (kabupatenInput) {
                kabupatenInput.disabled = false;
            }
        });
    }
    if (kabupatenInput) {
        kabupatenInput.addEventListener('blur', () => validateRequired(kabupatenInput, 'Kabupaten/Kota wajib dipilih'));
        kabupatenInput.addEventListener('change', () => clearFieldError(kabupatenInput));
    }
    
    // Relationship goal validation
    const relationshipGoalInputs = document.querySelectorAll('input[name="relationship_goal"]');
    if (relationshipGoalInputs.length > 0) {
        relationshipGoalInputs.forEach(input => {
            input.addEventListener('change', () => {
                const container = input.closest('.radio-group');
                if (container) {
                    const errorDiv = container.querySelector('.invalid-feedback');
                    if (errorDiv) {
                        errorDiv.style.display = 'none';
                    }
                }
            });
        });
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
    if (!birthDateInput) return false;
    
    if (!birthDateInput.value) {
        showFieldError(birthDateInput, 'Tanggal lahir wajib diisi');
        return false;
    }
    
    const birthDate = new Date(birthDateInput.value);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    const isValid = age >= 21;
    
    if (!isValid) {
        showFieldError(birthDateInput, 'Anda harus berusia minimal 21 tahun');
    } else {
        clearFieldError(birthDateInput);
    }
    
    return isValid;
}

function validateHeight() {
    const heightInput = document.getElementById('height_cm');
    if (!heightInput) return true;
    
    const height = parseInt(heightInput.value);
    const isValid = height >= 100 && height <= 250;
    
    if (!isValid && heightInput.value) {
        showFieldError(heightInput, 'Tinggi badan harus antara 100-250 cm');
    } else {
        clearFieldError(heightInput);
    }
    
    return isValid;
}

function validateWeight() {
    const weightInput = document.getElementById('weight_kg');
    if (!weightInput) return true;
    
    const weight = parseInt(weightInput.value);
    const isValid = weight >= 30 && weight <= 300;
    
    if (!isValid && weightInput.value) {
        showFieldError(weightInput, 'Berat badan harus antara 30-300 kg');
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
    
    // Handle special case for radio buttons and checkboxes
    const isRadioOrCheckbox = field.type === 'radio' || field.type === 'checkbox';
    const container = isRadioOrCheckbox ? field.closest('.radio-group, .checkbox-group') : field.parentNode;
    
    if (isRadioOrCheckbox && container) {
        container.classList.add('is-invalid');
    }
    
    let errorDiv = container.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        container.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Scroll to the error if it's not visible
    if (!isElementInViewport(field)) {
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Add a subtle shake animation to draw attention
    field.animate(
        [
            { transform: 'translateX(0)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(5px)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(0)' }
        ],
        {
            duration: 300,
            iterations: 1
        }
    );
}

function validateRequired(field, message) {
    if (!field.value) {
        showFieldError(field, message);
        return false;
    } else {
        clearFieldError(field);
        return true;
    }
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    // Handle special case for radio buttons and checkboxes
    const isRadioOrCheckbox = field.type === 'radio' || field.type === 'checkbox';
    const container = isRadioOrCheckbox ? field.closest('.radio-group, .checkbox-group') : field.parentNode;
    
    if (isRadioOrCheckbox && container) {
        container.classList.remove('is-invalid');
    }
    
    const errorDiv = container.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Helper function to check if an element is visible in the viewport
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
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
        showFieldError(photoInput, 'Pilih file gambar yang valid (JPG, PNG, GIF, WebP)');
        return false;
    }
    
    // Check file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showFieldError(photoInput, 'Ukuran file harus kurang dari 5MB');
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
        showError('Mohon periksa kembali data yang Anda masukkan');
        return;
    }
    
    console.log('Form validation passed, submitting...');
    
    // Show loading state
    showLoading(true);
    
    // Collect form data
    const formData = collectFormData();
    
    // Submit the form directly
    e.target.submit();
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
    // Create or update toast notification
    let toast = document.getElementById('errorToast');
    
    if (!toast) {
        // Create toast container if it doesn't exist
        toast = document.createElement('div');
        toast.id = 'errorToast';
        toast.className = 'error-toast';
        document.body.appendChild(toast);
        
        // Add toast styles if not already in the document
        if (!document.getElementById('toastStyles')) {
            const style = document.createElement('style');
            style.id = 'toastStyles';
            style.textContent = `
                .error-toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background-color: #dc3545;
                    color: white;
                    padding: 15px 25px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 9999;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    transform: translateY(-20px);
                    opacity: 0;
                    transition: transform 0.3s ease, opacity 0.3s ease;
                    max-width: 80%;
                }
                .error-toast.show {
                    transform: translateY(0);
                    opacity: 1;
                }
                .error-toast i {
                    font-size: 1.2rem;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Set toast content and show it
    toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    toast.classList.add('show');
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
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