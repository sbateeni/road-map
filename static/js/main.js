// Initialize Select2
$(document).ready(function() {
    $('#origin, #destination').select2({
        placeholder: 'ابحث عن مدينة أو منطقة...',
        allowClear: true,
        minimumInputLength: 2,
        ajax: {
            url: '/api/search_cities',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    query: params.term
                };
            },
            processResults: function(data) {
                return {
                    results: data.results || []
                };
            },
            cache: true
        }
    });
});

// Add event listeners for city search
$('#origin, #destination').on('select2:select', function(e) {
    const data = e.params.data;
    
    // Update the map to show the selected city
    if (data.latitude && data.longitude) {
        updateMap(data.latitude, data.longitude);
    }
});

// Get vehicle specs
async function getVehicleSpecs() {
    const brand = document.getElementById('brand').value;
    const model = document.getElementById('model').value;
    const year = document.getElementById('year').value;
    
    if (!brand || !model || !year) {
        alert('الرجاء إدخال جميع بيانات المركبة');
        return;
    }
    
    // Show loading state
    document.getElementById('vehicleSpecs').innerHTML = '<div class="loading">جاري جلب مواصفات المركبة...</div>';
    document.getElementById('vehicleSpecsCard').style.display = 'block';
    
    try {
        const response = await fetch('/api/get_vehicle_specs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ brand, model, year })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('vehicleSpecs').innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        displayVehicleSpecs(data.specs);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('vehicleSpecs').innerHTML = '<div class="error">حدث خطأ أثناء جلب مواصفات المركبة</div>';
    }
}

// Display vehicle specifications
function displayVehicleSpecs(specs) {
    let html = `
        <div class="specs-section">
            <h3>المواصفات الأساسية</h3>
            <p><strong>الماركة:</strong> ${specs.brand}</p>
            <p><strong>الموديل:</strong> ${specs.model}</p>
            <p><strong>سنة الصنع:</strong> ${specs.year}</p>
            <p><strong>استهلاك الوقود:</strong> ${specs.fuel_consumption} لتر/100 كم</p>
        </div>
        
        <div class="specs-section">
            <h3>المواصفات الفنية</h3>
            <p><strong>حجم المحرك:</strong> ${specs.engine_size} سي سي</p>
            <p><strong>عدد الأسطوانات:</strong> ${specs.cylinders}</p>
            <p><strong>ناقل الحركة:</strong> ${specs.transmission}</p>
            <p><strong>نوع الوقود:</strong> ${specs.fuel_type}</p>
        </div>
        
        <div class="specs-section">
            <h3>الأداء</h3>
            <p><strong>القوة الحصانية:</strong> ${specs.horsepower} حصان</p>
            <p><strong>عزم الدوران:</strong> ${specs.torque} نيوتن متر</p>
            <p><strong>التسارع (0-100 كم/س):</strong> ${specs.acceleration} ثانية</p>
            <p><strong>السرعة القصوى:</strong> ${specs.top_speed} كم/س</p>
            <p><strong>سعة خزان الوقود:</strong> ${specs.fuel_tank} لتر</p>
        </div>
        
        <div class="specs-section">
            <h3>السلامة</h3>
            <p><strong>تقييم السلامة:</strong> ${specs.safety_rating}</p>
            <p><strong>عدد الوسائد الهوائية:</strong> ${specs.airbags}</p>
            <p><strong>أنظمة السلامة:</strong> ${specs.safety_systems}</p>
        </div>
        
        <div class="specs-section">
            <h3>جدول الصيانة</h3>
            <p><strong>تغيير الزيت:</strong> كل ${specs.maintenance.oil_change.distance} أو ${specs.maintenance.oil_change.time}</p>
            <p><strong>تغيير الإطارات:</strong> كل ${specs.maintenance.tire_change.distance} أو ${specs.maintenance.tire_change.time}</p>
            <p><strong>الفحص الدوري:</strong> كل ${specs.maintenance.service.distance} أو ${specs.maintenance.service.time}</p>
        </div>
    `;
    
    document.getElementById('vehicleSpecs').innerHTML = html;
}

// Calculate route
async function calculateRoute() {
    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const routeType = document.getElementById('routeType').value;
    
    if (!origin || !destination) {
        alert('الرجاء اختيار نقاط البداية والنهاية');
        return;
    }
    
    // Show loading state
    document.getElementById('results').innerHTML = '<div class="loading">جاري حساب المسار...</div>';
    
    try {
        // Parse coordinates from the selected values
        const [startLat, startLng] = origin.split(',').map(Number);
        const [endLat, endLng] = destination.split(',').map(Number);
        
        const startCoords = { latitude: startLat, longitude: startLng };
        const endCoords = { latitude: endLat, longitude: endLng };
        
        const response = await fetch('/api/calculate_route', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: startCoords,
                end: endCoords,
                route_type: routeType
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('results').innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        // Update map
        if (data.geometry) {
            updateMapWithRoute(data.geometry);
        }
        
        // Update results
        displayRouteResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = '<div class="error">حدث خطأ أثناء حساب المسار</div>';
    }
}

// Update map with route
function updateMapWithRoute(geometry) {
    const mapContainer = document.getElementById('map');
    
    // Create a new map iframe with the route
    const mapFrame = document.createElement('iframe');
    mapFrame.src = `/map?geometry=${encodeURIComponent(JSON.stringify(geometry))}`;
    mapFrame.style.width = '100%';
    mapFrame.style.height = '400px';
    mapFrame.style.border = 'none';
    
    mapContainer.innerHTML = '';
    mapContainer.appendChild(mapFrame);
}

// Display route results
function displayRouteResults(data) {
    let html = `
        <div class="route-info">
            <h3>معلومات المسار</h3>
            <p><strong>المسافة:</strong> ${data.distance} كم</p>
            <p><strong>المدة المتوقعة:</strong> ${data.duration}</p>
            <p><strong>حالة المرور:</strong> <span class="traffic-level ${data.traffic_level.toLowerCase()}">${data.traffic_level}</span></p>
        </div>
    `;
    
    // Add fuel cost if available
    if (data.fuel_cost) {
        html += `
            <div class="fuel-cost">
                <h3>تكلفة الوقود</h3>
                <p><strong>كمية الوقود المطلوبة:</strong> ${data.fuel_cost.fuel_needed_liters} لتر</p>
                <p><strong>التكلفة الإجمالية:</strong> ${data.fuel_cost.total_cost} ₪</p>
            </div>
        `;
    }
    
    document.getElementById('results').innerHTML = html;
}

// Update map with coordinates
function updateMap(lat, lng) {
    const mapContainer = document.getElementById('map');
    const mapFrame = document.createElement('iframe');
    mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${lng-0.1},${lat-0.1},${lng+0.1},${lat+0.1}&layer=mapnik&marker=${lat},${lng}`;
    mapFrame.style.width = '100%';
    mapFrame.style.height = '400px';
    mapFrame.style.border = 'none';
    
    mapContainer.innerHTML = '';
    mapContainer.appendChild(mapFrame);
} 