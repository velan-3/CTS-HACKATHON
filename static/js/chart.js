// Initialize Charts (examples below for each type)
const chartsConfig = [
  { id: 'bloodBarChart1', type: 'bar', label: 'Blood Bar Chart 1', data: [10, 20, 15, 25, 30, 22], bgColor: 'rgba(255, 99, 132, 0.7)' },
  { id: 'bloodBarChart2', type: 'bar', label: 'Blood Bar Chart 2', data: [12, 18, 14, 22, 28, 26], bgColor: 'rgba(54, 162, 235, 0.7)' },
  { id: 'bloodBarChart3', type: 'bar', label: 'Blood Bar Chart 3', data: [16, 24, 19, 30, 34, 32], bgColor: 'rgba(75, 192, 192, 0.7)' },
  { id: 'bloodPieChart', type: 'pie', label: 'Blood Pie Chart', data: [50, 30, 20], bgColor: ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(75, 192, 192, 0.7)'] },

  { id: 'liverBarChart1', type: 'bar', label: 'Liver Bar Chart 1', data: [14, 25, 18, 28, 32, 29], bgColor: 'rgba(153, 102, 255, 0.7)' },
  { id: 'liverBarChart2', type: 'bar', label: 'Liver Bar Chart 2', data: [15, 26, 19, 30, 34, 32], bgColor: 'rgba(255, 206, 86, 0.7)' },
  { id: 'liverBarChart3', type: 'bar', label: 'Liver Bar Chart 3', data: [18, 29, 22, 33, 38, 35], bgColor: 'rgba(255, 159, 64, 0.7)' },
  { id: 'liverPieChart', type: 'pie', label: 'Liver Pie Chart', data: [40, 30, 30], bgColor: ['rgba(153, 102, 255, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(255, 159, 64, 0.7)'] },

  { id: 'kidneyBarChart1', type: 'bar', label: 'Kidney Bar Chart 1', data: [20, 30, 25, 35, 40, 37], bgColor: 'rgba(54, 162, 235, 0.7)' },
  { id: 'kidneyBarChart2', type: 'bar', label: 'Kidney Bar Chart 2', data: [22, 32, 27, 38, 43, 40], bgColor: 'rgba(255, 99, 132, 0.7)' },
  { id: 'kidneyBarChart3', type: 'bar', label: 'Kidney Bar Chart 3', data: [25, 35, 30, 42, 48, 44], bgColor: 'rgba(75, 192, 192, 0.7)' },
  { id: 'kidneyPieChart', type: 'pie', label: 'Kidney Pie Chart', data: [35, 40, 25], bgColor: ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)', 'rgba(75, 192, 192, 0.7)'] },

  { id: 'cholesterolBarChart1', type: 'bar', label: 'Cholesterol Bar Chart 1', data: [18, 28, 23, 33, 38, 35], bgColor: 'rgba(255, 159, 64, 0.7)' },
  { id: 'cholesterolBarChart2', type: 'bar', label: 'Cholesterol Bar Chart 2', data: [20, 30, 25, 35, 40, 37], bgColor: 'rgba(153, 102, 255, 0.7)' },
  { id: 'cholesterolBarChart3', type: 'bar', label: 'Cholesterol Bar Chart 3', data: [22, 32, 27, 38, 43, 40], bgColor: 'rgba(54, 162, 235, 0.7)' },
  { id: 'cholesterolPieChart', type: 'pie', label: 'Cholesterol Pie Chart', data: [30, 35, 35], bgColor: ['rgba(255, 159, 64, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(54, 162, 235, 0.7)'] }
];

// Function to create charts
chartsConfig.forEach(config => {
  new Chart(document.getElementById(config.id).getContext('2d'), {
    type: config.type,
    data: {
      labels: config.type === 'pie' ? ['Category 1', 'Category 2', 'Category 3'] : ['January', 'February', 'March', 'April', 'May', 'June'],
      datasets: [{
        label: config.label,
        data: config.data,
        backgroundColor: config.bgColor,
        borderColor: config.type === 'pie' ? [] : config.bgColor,
        borderWidth: config.type === 'pie' ? 0 : 1
      }]
    },
    options: {
      responsive: true,
      scales: config.type === 'pie' ? {} : {
        y: {
          beginAtZero: true
        }
      }
    }
  });
});

// Dropdown functionality
const optionMenu = document.querySelector(".select-menu"),
      selectBtn = optionMenu.querySelector(".select-btn"),
      options = optionMenu.querySelectorAll(".option"),
      sBtn_text = optionMenu.querySelector(".sBtn-text"),
      chartGrid = document.querySelector(".chart-grid"),
      charts = {
          blood: ["bloodBarChart1Container", "bloodBarChart2Container", "bloodBarChart3Container", "bloodPieChartContainer"],
          liver: ["liverBarChart1Container", "liverBarChart2Container", "liverBarChart3Container", "liverPieChartContainer"],
          kidney: ["kidneyBarChart1Container", "kidneyBarChart2Container", "kidneyBarChart3Container", "kidneyPieChartContainer"],
          cholesterol: ["cholesterolBarChart1Container", "cholesterolBarChart2Container", "cholesterolBarChart3Container", "cholesterolPieChartContainer"]
      };

// Hide all charts by default
document.querySelectorAll(".chart-container").forEach(chart => {
    chart.style.display = "none";
});

selectBtn.addEventListener("click", () => optionMenu.classList.toggle("active"));

options.forEach(option => {
    option.addEventListener("click", () => {
        let selectedOption = option.dataset.value;
        sBtn_text.innerText = option.querySelector(".option-text").innerText;

        optionMenu.classList.remove("active");

        // Reset chart visibility
        document.querySelectorAll(".chart-container").forEach(chart => {
            chart.style.display = "none";
        });

        // Show the selected charts
        charts[selectedOption].forEach(chartId => {
            document.getElementById(chartId).style.display = "block";
        });

        // Adjust layout if only one chart is displayed
        if (charts[selectedOption].length === 1) {
            chartGrid.classList.add("single-chart");
        } else {
            chartGrid.classList.remove("single-chart");
        }
    });
});
