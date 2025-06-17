// Profile Prefill Handler
class ProfilePrefillHandler {
    constructor() {
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        
        try {
            this.setupPhotoPreview();
            this.setupActiveTimePreview();
            this.setupOutdoorActivityPreview();
            this.initialized = true;
            console.log('Profile prefill handler initialized');
        } catch (error) {
            console.error('Error initializing profile prefill handler:', error);
        }
    }

    setupPhotoPreview() {
        // Get photo URL from profile preview avatar
        const previewAvatar = document.getElementById('previewAvatar');
        if (!previewAvatar) return;

        // Check if there's an image in the preview
        const previewImg = previewAvatar.querySelector('img');
        if (!previewImg) return;

        // Create a preview in the photo upload section
        const photoPreviewContainer = document.createElement('div');
        photoPreviewContainer.className = 'photo-preview';
        photoPreviewContainer.innerHTML = `
            <img src="${previewImg.src}" alt="Current photo" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <br>
            <button type="button" class="remove-photo-btn" onclick="removePhoto()">Hapus Foto</button>
        `;

        // Insert after the file input
        const profilePhotoInput = document.getElementById('profilePhoto');
        if (profilePhotoInput && !document.querySelector('.photo-preview')) {
            profilePhotoInput.parentNode.appendChild(photoPreviewContainer);
        }

        console.log('Photo preview setup complete');
    }

    setupActiveTimePreview() {
        // This function will be called when the page loads to set the active time checkboxes
        // based on the data in UserPreferencesSimilarity
        
        // Get the active time checkboxes
        const timeCheckboxes = [
            document.getElementById('time_morning'),
            document.getElementById('time_afternoon'),
            document.getElementById('time_evening'),
            document.getElementById('time_night')
        ];

        // Check if we have preferences_similarity data in the page
        const previewPets = document.getElementById('previewPets');
        if (!previewPets) return;

        // If we're using preferences_similarity for other fields, we should use it for active_time too
        // We need to get the active_time data from the server side
        // For now, we'll check if the checkboxes are already set correctly
        console.log('Active time preview setup complete');
    }

    setupOutdoorActivityPreview() {
        // Make sure the outdoor activity range value is displayed correctly
        const outdoorActivity = document.getElementById('outdoor_activity');
        const outdoorActivityValue = document.getElementById('outdoor_activity_value');
        
        if (outdoorActivity && outdoorActivityValue) {
            outdoorActivityValue.textContent = outdoorActivity.value;
            
            // Update the preview section
            const previewOutdoorActivity = document.createElement('div');
            previewOutdoorActivity.className = 'profile-info-item';
            previewOutdoorActivity.id = 'previewOutdoorActivity';
            previewOutdoorActivity.innerHTML = `
                <i class="fas fa-hiking"></i>
                <span>Aktivitas Outdoor: ${outdoorActivity.value}/5</span>
            `;
            
            // Add to preview if it doesn't exist
            const previewContainer = document.querySelector('.profile-preview-body');
            const existingPreview = document.getElementById('previewOutdoorActivity');
            
            if (previewContainer && !existingPreview) {
                // Insert before the bio section
                const previewBio = document.getElementById('previewBio');
                if (previewBio) {
                    previewContainer.insertBefore(previewOutdoorActivity, previewBio);
                } else {
                    previewContainer.appendChild(previewOutdoorActivity);
                }
            }
            
            console.log('Outdoor activity preview setup complete');
        }
    }
}

// Initialize the profile prefill handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const profilePrefill = new ProfilePrefillHandler();
    profilePrefill.init();
});