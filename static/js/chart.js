
//let charti = {};
const charts = {};

async function fetchChartsConfig() {
    const response = await fetch('/charts-config');
    return await response.json();
}

// function destroyChart(chartId) {
//     if (charts[chartId]) {
//         charts[chartId].destroy();
//         delete charts[chartId];
//     }
// }
function destroyChart(chartId) {
    if (charts[chartId]) {
        charts[chartId].destroy();
        delete charts[chartId];
    }
}


async function renderCharts() {
    const chartsConfig = await fetchChartsConfig();

    // Destroy existing charts
    Object.keys(charts).forEach(chartId => destroyChart(chartId));

    // Render new charts
    chartsConfig.forEach(config => {
        const ctx = document.getElementById(config.id).getContext('2d');
        const chart = new Chart(ctx, {
            type: config.type,
            data: {
                labels: config.labels,
                datasets: [{
                    label: config.label,
                    data: config.data,
                    backgroundColor: config.bgColor,
                    borderColor: config.borderColor || 'transparent',
                    borderWidth: config.borderWidth || 1,
                }]
            },
            options: {
                scales: {
                    y: {
                        min: config.yMin,
                        max: config.yMax,
                        beginAtZero: true
                    }
                },
                responsive: true
            }
        });
        charts[config.id] = chart; // Keep track of the new chart
    });
}

renderCharts();
