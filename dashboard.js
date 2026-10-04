document.addEventListener('DOMContentLoaded', function () {
    fetchStats();
    fetchChartData();
});

function fetchStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            if (document.getElementById('stat-total')) document.getElementById('stat-total').innerText = data.total;
            if (document.getElementById('stat-solved')) document.getElementById('stat-solved').innerText = data.solved;
            if (document.getElementById('stat-pending')) document.getElementById('stat-pending').innerText = data.pending;
            if (document.getElementById('stat-states')) document.getElementById('stat-states').innerText = data.states;
        })
        .catch(err => console.error('Error loading stats:', err));
}

function fetchChartData() {
    fetch('/api/charts-data')
        .then(res => res.json())
        .then(data => {
            renderChart('chartCategory', 'doughnut', data.categories.labels, data.categories.values, 'Crimes by Category');
            renderChart('chartTrends', 'line', data.trends.labels, data.trends.values, 'Yearly Crime Trends');
            renderChart('chartStates', 'bar', data.states.labels, data.states.values, 'Crimes by State');
            renderChart('chartStatus', 'pie', data.statuses.labels, data.statuses.values, 'Case Status Breakdown');
        })
        .catch(err => console.error('Error loading charts:', err));
}

function renderChart(canvasId, type, labels, values, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: [
                    '#2b580c', '#639a67', '#d8ebb5', '#d9bf77',
                    '#222831', '#393e46', '#00adb5', '#eeeeee'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}