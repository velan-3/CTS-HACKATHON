async function fetchChartsConfig() {
  const response = await fetch('/charts-config');
  return await response.json();
}

async function renderCharts() {
  const chartsConfig = await fetchChartsConfig();
  
  chartsConfig.forEach(config => {
      const ctx = document.getElementById(config.id).getContext('2d');
      new Chart(ctx, {
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
  });
}

renderCharts();