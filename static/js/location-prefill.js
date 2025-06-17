// Location Prefill Handler
class LocationPrefillHandler {
    constructor() {
        this.provinsiData = {};
        this.kabupatenData = {};
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        
        try {
            await this.loadProvinsiData();
            await this.prefillLocation();
            this.isInitialized = true;
        } catch (error) {
            console.error('Error initializing location prefill:', error);
        }
    }

    async loadProvinsiData() {
        try {
            const response = await fetch('/static/data_wilayah_indo/provinsi/provinsi.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.provinsiData = await response.json();
            console.log('Provinsi data loaded for prefill:', Object.keys(this.provinsiData).length, 'provinces');
        } catch (error) {
            console.error('Error loading provinsi data for prefill:', error);
            throw error;
        }
    }

    async loadKabupatenData(provinsiId) {
        try {
            const response = await fetch(`/static/data_wilayah_indo/kabupaten_kota/kab-${provinsiId}.json`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.kabupatenData[provinsiId] = data;
            console.log(`Kabupaten data loaded for prefill provinsi ${provinsiId}:`, Object.keys(data).length, 'kabupaten/kota');
            return data;
        } catch (error) {
            console.error(`Error loading kabupaten data for prefill provinsi ${provinsiId}:`, error);
            throw error;
        }
    }

    async prefillLocation() {
        const locationField = document.getElementById('location');
        const provinsiSelect = document.getElementById('provinsi');
        const kabupatenSelect = document.getElementById('kabupaten');

        if (!locationField || !provinsiSelect || !kabupatenSelect) {
            console.log('Location prefill elements not found');
            return;
        }

        const savedLocation = locationField.value;
        if (!savedLocation) {
            console.log('No saved location to prefill');
            return;
        }

        console.log('Attempting to prefill location:', savedLocation);

        // Parse saved location (format: "Kabupaten, Provinsi")
        const locationParts = savedLocation.split(', ');
        if (locationParts.length !== 2) {
            console.log('Invalid location format for prefill:', savedLocation);
            return;
        }

        const [kabupatenName, provinsiName] = locationParts;

        // Find provinsi ID by name
        const provinsiId = this.findProvinsiIdByName(provinsiName);
        if (!provinsiId) {
            console.log('Provinsi not found for prefill:', provinsiName);
            return;
        }

        // Set provinsi value
        provinsiSelect.value = provinsiId;
        console.log('Provinsi prefilled:', provinsiName, 'ID:', provinsiId);

        // Load and set kabupaten
        try {
            let kabupatenData = this.kabupatenData[provinsiId];
            if (!kabupatenData) {
                kabupatenData = await this.loadKabupatenData(provinsiId);
            }

            // Populate kabupaten options
            kabupatenSelect.innerHTML = '<option value="">Pilih Kabupaten/Kota</option>';
            Object.entries(kabupatenData).forEach(([id, name]) => {
                const option = document.createElement('option');
                option.value = id;
                option.textContent = name;
                option.setAttribute('data-name', name);
                kabupatenSelect.appendChild(option);
            });

            // Find kabupaten ID by name
            const kabupatenId = this.findKabupatenIdByName(kabupatenData, kabupatenName);
            if (kabupatenId) {
                kabupatenSelect.value = kabupatenId;
                kabupatenSelect.disabled = false;
                console.log('Kabupaten prefilled:', kabupatenName, 'ID:', kabupatenId);
            } else {
                console.log('Kabupaten not found for prefill:', kabupatenName);
            }

        } catch (error) {
            console.error('Error prefilling kabupaten:', error);
        }
    }

    findProvinsiIdByName(provinsiName) {
        for (const [id, name] of Object.entries(this.provinsiData)) {
            if (name.toLowerCase() === provinsiName.toLowerCase()) {
                return id;
            }
        }
        return null;
    }

    findKabupatenIdByName(kabupatenData, kabupatenName) {
        for (const [id, name] of Object.entries(kabupatenData)) {
            if (name.toLowerCase() === kabupatenName.toLowerCase()) {
                return id;
            }
        }
        return null;
    }
}

// Auto-initialize location prefill after wilayah handler is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for wilayah handler to initialize first
    setTimeout(async () => {
        if (window.wilayahHandler) {
            const prefillHandler = new LocationPrefillHandler();
            await prefillHandler.init();
        }
    }, 1000);
});