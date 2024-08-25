// Visualization

// Line Chart
const lineChart = new Chart(document.getElementById('lineChart').getContext('2d'), {
  type: 'line',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May', 'June'],
    datasets: [{
      label: 'Patients Treated',
      data: [10, 20, 15, 25, 30, 22],
      borderColor: 'rgba(75, 192, 192, 1)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      fill: true,
      tension: 0.3,
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Bar Chart
const barChart = new Chart(document.getElementById('barChart').getContext('2d'), {
  type: 'bar',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May', 'June'],
    datasets: [{
      label: 'Surgeries Performed',
      data: [8, 15, 12, 18, 20, 17],
      backgroundColor: 'rgba(54, 162, 235, 0.7)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Clustered Bar Chart
const clusteredBarChart = new Chart(document.getElementById('clusteredBarChart').getContext('2d'), {
  type: 'bar',
  data: {
    labels: ['Cardiology', 'Neurology', 'Orthopedics', 'Oncology'],
    datasets: [
      {
        label: '2019',
        data: [40, 30, 20, 25],
        backgroundColor: 'rgba(255, 99, 132, 0.7)',
      },
      {
        label: '2020',
        data: [35, 25, 15, 20],
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
      },
      {
        label: '2021',
        data: [50, 45, 35, 30],
        backgroundColor: 'rgba(255, 206, 86, 0.7)',
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Stacked Bar Chart
const stackedBarChart = new Chart(document.getElementById('stackedBarChart').getContext('2d'), {
  type: 'bar',
  data: {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        label: 'Cardiology',
        data: [50, 60, 40, 70],
        backgroundColor: 'rgba(75, 192, 192, 0.7)',
      },
      {
        label: 'Neurology',
        data: [30, 40, 35, 50],
        backgroundColor: 'rgba(153, 102, 255, 0.7)',
      },
      {
        label: 'Orthopedics',
        data: [20, 25, 30, 35],
        backgroundColor: 'rgba(255, 159, 64, 0.7)',
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        beginAtZero: true,
      }
    }
  }
});

// Dropdown functionality
const optionMenu = document.querySelector(".select-menu"),
      selectBtn = optionMenu.querySelector(".select-btn"),
      options = optionMenu.querySelectorAll(".option"),
      sBtn_text = optionMenu.querySelector(".sBtn-text"),
      chartGrid = document.querySelector(".chart-grid"),
      charts = {
          all: ["lineChartContainer", "barChartContainer", "clusteredBarChartContainer", "stackedBarChartContainer"],
          heart: ["lineChartContainer"],
          kidney: ["barChartContainer"],
          liver: ["stackedBarChartContainer"]
      };

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


