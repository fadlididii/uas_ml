class WilayahLocalHandler {
    constructor(options = {}) {
        this.provinsiSelectId = options.provinsiSelectId || 'provinsi';
        this.kabupatenSelectId = options.kabupatenSelectId || 'kabupaten';
        this.locationHiddenId = options.locationHiddenId || 'location';
        
        this.provinsiData = {};
        this.kabupatenData = {};
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadProvinsiData();
            this.setupEventListeners();
            this.populateProvinsi();
        } catch (error) {
            console.error('Error initializing wilayah handler:', error);
        }
    }
    
    async loadProvinsiData() {
        try {
            const response = await fetch('/static/data_wilayah_indo/provinsi/provinsi.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.provinsiData = await response.json();
            console.log('Provinsi data loaded:', Object.keys(this.provinsiData).length, 'provinces');
        } catch (error) {
            console.error('Error loading provinsi data:', error);
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
            console.log(`Kabupaten data loaded for provinsi ${provinsiId}:`, Object.keys(data).length, 'kabupaten/kota');
            return data;
        } catch (error) {
            console.error(`Error loading kabupaten data for provinsi ${provinsiId}:`, error);
            return {};
        }
    }
    
    populateProvinsi() {
        const provinsiSelect = document.getElementById(this.provinsiSelectId);
        if (!provinsiSelect) {
            console.error('Provinsi select element not found');
            return;
        }
        
        // Clear existing options except the first one
        provinsiSelect.innerHTML = '<option value="">Pilih Provinsi</option>';
        
        // Add provinsi options
        Object.entries(this.provinsiData).forEach(([id, name]) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            provinsiSelect.appendChild(option);
        });
        
        console.log('Provinsi options populated');
    }
    
    async populateKabupaten(provinsiId) {
        const kabupatenSelect = document.getElementById(this.kabupatenSelectId);
        if (!kabupatenSelect) {
            console.error('Kabupaten select element not found');
            return;
        }
        
        // Clear existing options
        kabupatenSelect.innerHTML = '<option value="">Pilih Kabupaten/Kota</option>';
        kabupatenSelect.disabled = true;
        
        if (!provinsiId) {
            return;
        }
        
        try {
            // Load kabupaten data if not already loaded
            let kabupatenData = this.kabupatenData[provinsiId];
            if (!kabupatenData) {
                kabupatenData = await this.loadKabupatenData(provinsiId);
            }
            
            // Add kabupaten options
            Object.entries(kabupatenData).forEach(([id, name]) => {
                const option = document.createElement('option');
                option.value = id;
                option.textContent = name;
                option.setAttribute('data-name', name);
                kabupatenSelect.appendChild(option);
            });
            
            kabupatenSelect.disabled = false;
            console.log(`Kabupaten options populated for provinsi ${provinsiId}`);
        } catch (error) {
            console.error('Error populating kabupaten:', error);
        }
    }
    
    updateLocationField() {
        const provinsiSelect = document.getElementById(this.provinsiSelectId);
        const kabupatenSelect = document.getElementById(this.kabupatenSelectId);
        const locationField = document.getElementById(this.locationHiddenId);
        
        if (!provinsiSelect || !kabupatenSelect || !locationField) {
            console.error('Required elements not found for location update');
            return;
        }
        
        if (provinsiSelect.value && kabupatenSelect.value) {
            const provinsiText = provinsiSelect.options[provinsiSelect.selectedIndex].text;
            const kabupatenText = kabupatenSelect.options[kabupatenSelect.selectedIndex].getAttribute('data-name') || 
                                kabupatenSelect.options[kabupatenSelect.selectedIndex].text;
            
            const location = `${kabupatenText}, ${provinsiText}`;
            locationField.value = location;
            
            console.log('Location updated:', location);
            
            // Trigger change event for real-time preview updates
            locationField.dispatchEvent(new Event('change'));
        } else {
            locationField.value = '';
        }
    }
    
    setupEventListeners() {
        const provinsiSelect = document.getElementById(this.provinsiSelectId);
        const kabupatenSelect = document.getElementById(this.kabupatenSelectId);
        
        if (provinsiSelect) {
            provinsiSelect.addEventListener('change', async (e) => {
                const provinsiId = e.target.value;
                await this.populateKabupaten(provinsiId);
                this.updateLocationField();
            });
        }
        
        if (kabupatenSelect) {
            kabupatenSelect.addEventListener('change', () => {
                this.updateLocationField();
            });
        }
        
        console.log('Event listeners setup complete');
    }
}

// Auto-initialize if elements are present
document.addEventListener('DOMContentLoaded', () => {
    const provinsiSelect = document.getElementById('provinsi');
    const kabupatenSelect = document.getElementById('kabupaten');
    
    if (provinsiSelect && kabupatenSelect) {
        window.wilayahHandler = new WilayahLocalHandler();
    }
});