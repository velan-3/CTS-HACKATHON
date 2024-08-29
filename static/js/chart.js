
/*
const chartsConfig = [
  // Blood Test Results (CBC)
  {
    id: 'cbcChart',
    type: 'bar',
    label: 'CBC Results',
    data: [11.2, 33.5, 3.85, 87.2, 29.2, 33.5, 15, 6810, 270000],
    bgColor: 'rgba(54, 162, 235, 0.7)',
    labels: ['Hemoglobin', 'PCV', 'RBC', 'MCV', 'MCH', 'MCHC', 'RDW', 'TLC', 'Platelets'],
    yMin: 0,
    yMax: 300000,
  },
  {
    id: 'dlcChart',
    type: 'bar',
    label: 'DLC Percentages',
    data: [58.6, 24.8, 6.6, 9.6, 0.4],
    bgColor: ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
    labels: ['Neutrophils', 'Lymphocytes', 'Eosinophils', 'Monocytes', 'Basophils'],
    yMin: 0,
    yMax: 100,
  },
  {
    id: 'nlrChart',
    type: 'line',
    label: 'NLR',
    data: [2.36],
    bgColor: 'rgba(255, 206, 86, 0.7)',
    labels: ['NLR'],
    yMin: 0,
    yMax: 5,
  },

  // Liver Function Test (LFT) Results
  {
    id: 'lftBarChart',
    type: 'bar',
    label: 'LFT Results',
    data: [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
    bgColor: 'rgba(153, 102, 255, 0.7)',
    labels: ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Total Protein', 'Albumin', 'Globulin', 'A/G Ratio'],
    yMin: 0,
    yMax: 100,
  },
  {
    id: 'lftRadarChart',
    type: 'radar',
    label: 'LFT Status',
    data: [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
    bgColor: 'rgba(255, 159, 64, 0.7)',
    labels: ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Total Protein', 'Albumin', 'Globulin', 'A/G Ratio'],
    yMin: 0,
    yMax: 100,
  },

  // Kidney Function Test (KFT) Results
  {
    id: 'kftBarChart',
    type: 'bar',
    label: 'KFT Results',
    data: [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
    bgColor: 'rgba(75, 192, 192, 0.7)',
    labels: ['Creatinine', 'Urea', 'BUN', 'Uric Acid', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
    yMin: 0,
    yMax: 150,
  },
  {
    id: 'kftViolinChart',
    type: 'line', // Note: Actual Violin Plot is complex, use line chart for simplicity here.
    label: 'KFT Distribution',
    data: [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
    bgColor: 'rgba(54, 162, 235, 0.7)',
    labels: ['Creatinine', 'Urea', 'BUN', 'Uric Acid', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
    yMin: 0,
    yMax: 150,
  },

  // Cholesterol Test Results
  {
    id: 'cholesterolPieChart',
    type: 'pie',
    label: 'Cholesterol Distribution',
    data: [127, 48, 60.76, 18.74],
    bgColor: ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
    labels: ['Total Cholesterol', 'HDL', 'LDL', 'VLDL'],
  },
  {
    id: 'cholesterolBarChart',
    type: 'bar',
    label: 'Cholesterol Test Results',
    data: [127, 94, 48, 80, 60.76, 18.74],
    bgColor: 'rgba(153, 102, 255, 0.7)',
    labels: ['Total Cholesterol', 'Triglycerides', 'HDL', 'Non-HDL', 'LDL', 'VLDL'],
    yMin: 0,
    yMax: 200,
  },
  {
    id: 'cholesterolLineChart',
    type: 'line',
    label: 'Cholesterol/HDL Ratio & Atherogenic Index',
    data: [2.67, 0.01],
    bgColor: 'rgba(255, 159, 64, 0.7)',
    labels: ['Cholesterol/HDL Ratio', 'Atherogenic Index'],
    yMin: 0,
    yMax: 5,
  },
];

// Initialize Charts
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
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
      }]
    },
    options: {
      scales: {
        y: {
          min: config.yMin,
          max: config.yMax,
        }
      }
    }
  });
});

*/

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