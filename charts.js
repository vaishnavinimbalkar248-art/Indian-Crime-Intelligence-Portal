document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/chart-data')
        .then(response => response.json())
        .then(data => {
            renderCrimeTypeChart(data.crime_type_freq);
            renderYearTrendChart(data.year_trend);
            renderMonthlyTrendChart(data.monthly_trend);
            renderLocationChart(data.location_counts);
            renderDayNightChart(data.day_night_counts);
            renderCrimeDistributionChart(data.crime_distribution);
            renderArrestChart(data.arrest_counts);
            renderAgeHistogram(data.age_binned);
            renderAgeBoxPlot(data.raw_ages);
            renderStateCrimeHeatmap(data.heatmap_data);
        })
        .catch(error => console.error('Error fetching chart data:', error));
});

// Chart 1: Crime Type Frequency
function renderCrimeTypeChart(data) {
    new Chart(document.getElementById('chartCrimeType').getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Incidents', data: Object.values(data), backgroundColor: '#0b1e36', borderRadius: 6 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

// Chart 2: Year-wise Crime Trend
function renderYearTrendChart(data) {
    new Chart(document.getElementById('chartYearTrend').getContext('2d'), {
        type: 'line',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Crimes per Year', data: Object.values(data), borderColor: '#2563eb', backgroundColor: 'rgba(37, 99, 235, 0.1)', fill: true, tension: 0.3 }]
        },
        options: { responsive: true }
    });
}

// Chart 3: Monthly Crime Trend
function renderMonthlyTrendChart(data) {
    new Chart(document.getElementById('chartMonthlyTrend').getContext('2d'), {
        type: 'line',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Monthly Crimes', data: Object.values(data), borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.3 }]
        },
        options: { responsive: true }
    });
}

// Chart 4: Crime by Location
function renderLocationChart(data) {
    new Chart(document.getElementById('chartLocation').getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Incidents', data: Object.values(data), backgroundColor: '#f59e0b', borderRadius: 6 }]
        },
        options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
    });
}

// Chart 5: Day vs Night Crime
function renderDayNightChart(data) {
    new Chart(document.getElementById('chartDayNight').getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Incidents', data: Object.values(data), backgroundColor: ['#3b82f6', '#1e1b4b'], borderRadius: 6 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

// Chart 6: Crime Type Distribution (Doughnut)
function renderCrimeDistributionChart(data) {
    new Chart(document.getElementById('chartCrimeDistribution').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#0b1e36', '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Chart 7: Arrest Statistics (Pie)
function renderArrestChart(data) {
    new Chart(document.getElementById('chartArrest').getContext('2d'), {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#10b981', '#ef4444']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Chart 8: Age Distribution (Histogram)
function renderAgeHistogram(data) {
    new Chart(document.getElementById('chartAgeHistogram').getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{ label: 'Count', data: Object.values(data), backgroundColor: '#8b5cf6', borderRadius: 6 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

// Chart 9: Age Box Plot (Plotly)
function renderAgeBoxPlot(data) {
    const trace = {
        y: data,
        type: 'box',
        name: 'Age Distribution',
        marker: { color: '#0b1e36' },
        boxpoints: 'outliers'
    };
    const layout = { margin: { t: 20, b: 30, l: 40, r: 20 }, autosize: true };
    Plotly.newPlot('chartAgeBoxPlot', [trace], layout, { responsive: true, displayModeBar: false });
}

// Chart 10: State vs Crime Type Heatmap (Plotly)
function renderStateCrimeHeatmap(data) {
    const trace = {
        z: data.z,
        x: data.crimes,
        y: data.states,
        type: 'heatmap',
        colorscale: 'Blues'
    };
    const layout = { margin: { t: 20, b: 80, l: 120, r: 20 }, autosize: true };
    Plotly.newPlot('chartStateCrimeHeatmap', [trace], layout, { responsive: true, displayModeBar: false });
}