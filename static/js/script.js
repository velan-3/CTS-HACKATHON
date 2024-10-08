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

  // Hide the modal when "Summarize" is clicked
  modal.style.display = "none";
  pdfViewer.innerHTML = '';

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
          let sum = data.summary
          //let formattedSummary = sum.split("\n").map(line => line).join("\n\n");
          const structuredSummary = sum;

          // Combine the summary message and structured summary into one string
          const fullSummaryText = summaryMessage + structuredSummary;

          // Clear previous content in the PDF viewer
          pdfViewer.innerHTML = '';
          const links = document.querySelectorAll('.nav_link.disabled');
  
          // Remove the 'disabled' class to activate them
          links.forEach(link => {
              link.classList.remove('disabled');
          });
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

document.getElementById('consultationlink').addEventListener('click', function(event) {
    event.preventDefault();
    fetch('/consultation') 
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); 
        })
        .then(data => {
            console.log(data); 
            const lines = data.split('\n');
            const dataContainer = document.getElementById('fetched-data');
            dataContainer.innerHTML= '';
            lines.forEach(function(line) {
              const p = document.createElement('p');  // Create a <p> element
              p.textContent = line.trim();            // Set the text content to the current line
              dataContainer.appendChild(p);       // Append the <p> element to the div
          });
            //dataContainer.innerHTML = `<p>${data}</p>`;;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

})

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
      setTimeout(type, 5); // Adjust speed here
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
  const searchQuery = document.getElementById('searchQuery').value;

  // Show the loader
  document.getElementById("loader").style.display = "block";

  // Hide search results while loading
  document.getElementById("searchResults").style.display = "none";

  // Send the search query to the Flask backend
  fetch('/process-query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: searchQuery })
  })
  .then(response => response.json())
  .then(data => {
    // Hide the loader when data is received
    document.getElementById("loader").style.display = "none";

    // Display the result in the searchResults div
    var resultsDiv = document.getElementById("searchResults");

    // Clear previous result
    resultsDiv.innerHTML = "";

    // Add a container for the typewriter effect
    var resultText = document.createElement("p");
    resultText.classList.add("typewriter-text"); // Add class for styling
    resultsDiv.appendChild(resultText);

    const answer = data.result; 
    // Start typewriter effect
    typeWriter(answer, resultText);

    // Display the results div
    resultsDiv.style.display = "block";
  })
  .catch(error => {
    console.error('Error:', error);
    // Hide the loader in case of an error
    document.getElementById("loader").style.display = "none";
  });
});


let cachedPredictions = []; // Array to store fetched predictions
let currentIndex = 0;
// Function to fetch predictions from the Flask backend
async function fetchPredictions() {
    try {
        const response = await fetch('/prediction'); // Fetch prediction data from the Flask endpoint
        const predictions = await response.json(); // Parse JSON response
        cachedPredictions = predictions; // Cache the fetched data
        updatePredictionUI(cachedPredictions); // Update UI with the first prediction
    } catch (error) {
        console.error('Error fetching prediction data:', error);
    }
}

function updatePredictionUI(predictions) {
  if (predictions.length > 0) {
    // Use the current index to select the prediction
    const prediction = predictions[currentIndex];

    // Update the image and prediction details
    document.getElementById('prediction-image').src = prediction.image;
    document.getElementById('predicted-organ').innerText = `Predicted Organ: ${prediction.organ}`;
    document.getElementById('predicted-disease').innerText = `Predicted Disease: ${prediction.disease}`;
    document.getElementById('disease-description').innerText = prediction.description;

    // Update the index for the next call
    currentIndex = (currentIndex + 1) % predictions.length;
} else {
    // Handle the case where no predictions are available
    document.getElementById('prediction-image').src = ''; // Clear image
    document.getElementById('predicted-organ').innerText = 'No predictions available';
    document.getElementById('predicted-disease').innerText = '';
    document.getElementById('disease-description').innerText = '';
}
}

// Add event listener to the "Prediction" link
document.getElementById('PredictionLink').addEventListener('click', function(event) {
  // Prevent default link action if needed
  event.preventDefault();

  // Fetch and update predictions when the link is clicked
  fetchPredictions();
});

// Add an event listener to the "Change Prediction" button to show a different prediction
document.getElementById('changePredictionBtn').addEventListener('click', function() {
  if (cachedPredictions.length > 0) {
      updatePredictionUI(cachedPredictions); // Update UI with a new prediction from the cached data
  }
});

