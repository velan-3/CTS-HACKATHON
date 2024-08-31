const body = document.querySelector("body");
const sidebar = document.querySelector(".sidebar");


if (window.innerWidth < 768) {
  sidebar.classList.add("close");
} else {
  sidebar.classList.remove("close");
}

// Get all the nav links and content sections
const navLinks = document.querySelectorAll('.nav_link');
const contentSections = document.querySelectorAll('.content_section');

// Add click event listeners to all nav links
navLinks.forEach((link) => {
  link.addEventListener('click', function () {
    // Remove active class from all sections
    contentSections.forEach((section) => {
      section.classList.remove('active');
      section.style.display = 'none';
    });

    // Remove active class from all nav links
    navLinks.forEach((link) => {
      link.classList.remove('active');
    });

    // Add active class to the clicked nav link
    this.classList.add('active');

    // Show the corresponding content section
    const sectionId = this.querySelector('.navlink').textContent.toLowerCase();
    document.getElementById(sectionId).style.display = 'block';
  });
});

// Set the default active section
document.getElementById('home').style.display = 'block';
navLinks[0].classList.add('active');

document.getElementById('viewBtn').addEventListener('click', function () {
  const pdfFile = document.getElementById('pdfUpload').files[0];
  if (pdfFile) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const pdfData = new Uint8Array(e.target.result);
      displayPDF(pdfData);
    };
    reader.readAsArrayBuffer(pdfFile);
  } else {
    alert('Please upload a PDF file.');
  }
});
//PDF TRANSFERING TO PYTHON
document.getElementById('pdfUpload').addEventListener('change', function () {
  const pdfFile = document.getElementById('pdfUpload').files[0];
  const fileName = pdfFile?.name || 'No file chosen';
  document.getElementById('fileName').textContent = fileName;

  if (pdfFile) {
    const formData = new FormData();
    formData.append('pdf', pdfFile); // Correctly append the file to the formData object
    console.log("before upload");
    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      console.log('PDF uploaded and processed:', data);
      // You can handle the response here, e.g., displaying a summary in the `pdfViewer` div
    })
    .catch(error => console.error('Error:', error));
  } else {
    alert('Please upload a PDF file.');
  }
});

// Event listener for the 'Summarize' button
document.getElementById('summarizeBtn').addEventListener('click', function () {
  const pdfFile = document.getElementById('pdfUpload').files[0];
  const pdfViewer = document.getElementById('pdfViewer');
  const loader = document.querySelector('.loader');  // Reference to the loader element

  // Show the loader animation
  loader.style.display = 'block';

  // Check if a PDF file has been uploaded
  if (pdfFile) {
      const fileName = pdfFile.name;
      const summaryMessage = `Summarized report for ${fileName}:\n`;

      // Send a request to the Flask server to trigger summarization
      fetch('/summarize', {
          method: 'POST',
          body: new FormData(document.getElementById('uploadForm')), // Include the PDF file in the request
      })
      .then(response => response.json())
      .then(data => {
          console.log("Details fetched");

          // Assume the server sends back the summarized content in 'data.summary'
          const structuredSummary = data.summary;

          // Combine the summary message and structured summary into one string
          const fullSummaryText = summaryMessage + structuredSummary;

          // Clear previous content in the PDF viewer
          pdfViewer.innerHTML = '';

          // Create and append the typewriter effect container
          const summaryTile = document.createElement('div');
          summaryTile.classList.add('full-width-tile');  // Ensure full-width-tile class is added
          pdfViewer.appendChild(summaryTile);

          const summaryText = document.createElement('div');
          summaryText.classList.add('typewriter-text');
          summaryTile.appendChild(summaryText);

          console.log("Typewriter function called");

          // Hide the loader as we start generating the content
          loader.style.display = 'none';

          // Apply the typewriter effect to the combined text
          typeWriter(fullSummaryText, summaryText, function(){
              document.getElementById('downloadPdfBtn').style.display = 'block';
          });
      })
      .catch(error => {
          console.error('Error:', error);
          
          // Hide the loader in case of an error
          loader.style.display = 'none';
      });
  } else {
      alert('Please upload a PDF file.');

      // Hide the loader if no file is uploaded
      loader.style.display = 'none';
  }
});


// Event listener for the 'Download PDF' button
document.getElementById('downloadPdfBtn').addEventListener('click', function () {
  const summaryElement = document.querySelector('.full-width-tile');
  downloadPDF(summaryElement);
});

document.getElementById('visualizationLink').addEventListener('click', function(event) {
  event.preventDefault(); // Prevent default link behavior
  
  // Show the chart container
  //document.getElementById('chartContainer').style.display = 'block';
  
  // Render the chart
  console.log("Executed")
  renderCharts();
});

// async function fetchChartsConfig() {
//   const response = await fetch('/charts-config');
//   return await response.json();
// }

// async function renderCharts() {
//   const chartsConfig = await fetchChartsConfig();
  
//   chartsConfig.forEach(config => {
//       const ctx = document.getElementById(config.id).getContext('2d');
//       new Chart(ctx, {
//           type: config.type,
//           data: {
//               labels: config.labels,
//               datasets: [{
//                   label: config.label,
//                   data: config.data,
//                   backgroundColor: config.bgColor,
//                   borderColor: config.borderColor || 'transparent',
//                   borderWidth: config.borderWidth || 1,
//               }]
//           },
//           options: {
//               scales: {
//                   y: {
//                       min: config.yMin,
//                       max: config.yMax,
//                       beginAtZero: true
//                   }
//               },
//               responsive: true
//           }
//       });
//   });
// }


// Function to handle PDF download
function downloadPDF(element) {
  const options = {
    margin: 0.5, // Adjusted margin for the PDF
    filename: 'summarized-report.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  };

  html2pdf().from(element).set(options).save();
}

// Function for typewriter effect on text
function typeWriter(text, element, callback) {
  let index = 0;
  element.innerHTML = ''; // Clear existing content

  function type() {
    if (index < text.length) {
      element.innerHTML += text.charAt(index);
      index++;
      setTimeout(type, 10); // Adjust speed here
    } else if (callback) {
      callback(); // Call the callback function after typing is complete
    }
  }
  type();
}

// Function for typewriter effect on a single string of text
function typeWriterSingleText(text, parentElement, callback) {
  const lines = text.split('\n'); // Split text by new lines to simulate structured content
  let lineIndex = 0;

  function typeLine() {
    if (lineIndex < lines.length) {
      const lineData = lines[lineIndex].trim();
      let lineElement;

      // Determine element type based on simple detection
      if (lineData.startsWith('h3:')) {
        lineElement = document.createElement('h3');
        lineElement.innerHTML = ''; // Start with empty content
        parentElement.appendChild(lineElement);
        typeWriter(lineData.slice(3), lineElement, function () {
          lineIndex++;
          typeLine(); // Move to the next line after the current one is done
        });
      } else if (lineData.startsWith('p:')) {
        lineElement = document.createElement('p');
        lineElement.innerHTML = ''; // Start with empty content
        parentElement.appendChild(lineElement);
        typeWriter(lineData.slice(2), lineElement, function () {
          lineIndex++;
          typeLine(); // Move to the next line after the current one is done
        });
      } else if (lineData.startsWith('ul:')) {
        lineElement = document.createElement('ul');
        parentElement.appendChild(lineElement);

        const listItems = lineData.slice(3).split(';').map(item => item.trim());

        let listIndex = 0;

        function typeListItem() {
          if (listIndex < listItems.length) {
            const listItem = document.createElement('li');
            listItem.innerHTML = ''; // Start with empty content
            lineElement.appendChild(listItem);

            typeWriter(listItems[listIndex], listItem, function () {
              listIndex++;
              typeListItem(); // Move to the next list item
            });
          } else {
            lineIndex++;
            typeLine(); // Move to the next content block after the list is done
          }
        }

        typeListItem(); // Start typing the list items
      } else {
        // If no specific element type, assume paragraph
        lineElement = document.createElement('p');
        lineElement.innerHTML = lineData; // Insert the line content
        parentElement.appendChild(lineElement);
        lineIndex++;
        typeLine(); // Move to the next line
      }
    } else if (callback) {
      callback(); // Call the callback function if provided after all lines are done
    }
  }

  typeLine();
}


function displayPDF(pdfData) {
  pdfjsLib.getDocument(pdfData).promise.then(function (pdf) {
    const pdfViewer = document.getElementById('pdfViewer');
    pdfViewer.innerHTML = '';

    for (let i = 1; i <= pdf.numPages; i++) {
      pdf.getPage(i).then(function (page) {
        const scale = 1.5;
        const viewport = page.getViewport({ scale: scale });

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        const tileWidth = 300; // Adjusted value
        const scaleX = tileWidth / viewport.width;
        const scaledViewport = page.getViewport({ scale: scaleX });

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;

        const renderContext = {
          canvasContext: context,
          viewport: scaledViewport
        };

        page.render(renderContext).promise.then(function () {
          const tile = document.createElement('div');
          tile.className = 'pdf_tile';
          tile.appendChild(canvas);
          pdfViewer.appendChild(tile);
        });
      });
    }
  });
}

// Get modal elements
const modal = document.getElementById("pdfModal");
const modalCanvas = document.getElementById("modalCanvas");
const modalFileName = document.getElementById("modalFileName");
const closeModal = document.querySelector(".close");

// Function to show modal with detailed PDF view
function showModal(page, fileName) {
  // Set the file name in the modal
  modalFileName.textContent = fileName;

  // Render the selected page into the modal canvas
  const context = modalCanvas.getContext("2d");
  const viewport = page.getViewport({ scale: 2 }); // Adjust scale if needed
  modalCanvas.width = viewport.width;
  modalCanvas.height = viewport.height;

  const renderContext = {
    canvasContext: context,
    viewport: viewport
  };
  page.render(renderContext);

  // Show the modal
  modal.style.display = "block";
}

// Event listener to close the modal
closeModal.addEventListener("click", function () {
  modal.style.display = "none";
});

// Close modal if user clicks outside the modal content
window.addEventListener("click", function (event) {
  if (event.target === modal) {
    modal.style.display = "none";
  }
});

// Modify the existing displayPDF function to attach click events to tiles
function displayPDF(pdfData) {
  pdfjsLib.getDocument(pdfData).promise.then(function (pdf) {
    const pdfViewer = document.getElementById('pdfViewer');
    pdfViewer.innerHTML = '';

    for (let i = 1; i <= pdf.numPages; i++) {
      pdf.getPage(i).then(function (page) {
        const scale = 1.2;
        const viewport = page.getViewport({ scale: scale });

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        const renderContext = {
          canvasContext: context,
          viewport: viewport
        };

        page.render(renderContext).promise.then(function () {
          const tile = document.createElement('div');
          tile.className = 'pdf_tile';
          tile.appendChild(canvas);
          pdfViewer.appendChild(tile);

          // Add click event to each tile to show the modal
          tile.addEventListener('click', function () {
            showModal(page, document.getElementById('pdfUpload').files[0]?.name || 'PDF Report');
          });
        });
      });
    }
  });
}

// JavaScript to handle the search functionality
document.getElementById("searchBtn").addEventListener("click", function () {
  var query = document.getElementById("searchQuery").value;
  var resultsDiv = document.getElementById("searchResults");

  // Clear previous result
  resultsDiv.innerHTML = "";

  // Add a container for the typewriter effect
  var resultText = document.createElement("p");
  resultText.classList.add("typewriter-text"); // Add class for styling
  resultsDiv.appendChild(resultText);

  var sample = "The patient is a 30-year-old male. The blood test results indicate a Hemoglobin level of 15.00 g/dL, Packed Cell Volume (PCV) of 45.00%, RBC count of 4.50 mill/mm3, Mean Corpuscular Volume (MCV) of 90.00 fL, Mean Corpuscular Hemoglobin (MCH) of 32.00 pg, Mean Corpuscular Hemoglobin Concentration (MCHC) of 33.00 g/dL, and Red Cell Distribution Width (RDW) of 14.00%.The liver and kidney panel results show a Creatinine level of 118 mg/dL, Estimated Glomerular Filtration Rate (eGFR) of >59 mL/min/1.73m2, Urea level of 9.34 mg/dL, Urea Nitrogen in Blood of 10 mg/dL, Uric Acid level of 11.0 mg/dL, AST (SGOT) level of 21.0 U/L, and ALT (SGPT) level of 5.00 U/L. The eGFR falls under the G1 category (normal) according to the KDIGO Guideline 2012. The BUN/Creatinine ratio is 10.The key findings from the tests reveal that the patient's kidney function is normal, as indicated by the eGFR value. However, the liver enzyme levels, specifically AST and ALT, are slightly elevated. This could suggest liver damage or inflammation. Further investigation and clinical correlation are required to determine the cause and implications for the patient's health.Based on the test results, the doctor may recommend additional tests to evaluate liver function more thoroughly, such as a liver ultrasound or a liver biopsy. The patient should also be advised to avoid alcohol consumption and maintain a healthy diet to support liver health. Regular follow-up appointments and monitoring of liver enzyme levels are essential to assess the progression or resolution of liver damage."
  // Start typewriter effect
  typeWriter("Summary of " + query + ": " + sample, resultText);

  // Display the results div
  resultsDiv.style.display = "block";
});
