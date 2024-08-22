const inputs = document.querySelectorAll(".input");


function addcl(){
	let parent = this.parentNode.parentNode;
	parent.classList.add("focus");
}

function remcl(){
	let parent = this.parentNode.parentNode;
	if(this.value == ""){
		parent.classList.remove("focus");
	}
}


inputs.forEach(input => {
	input.addEventListener("focus", addcl);
	input.addEventListener("blur", remcl);
});

document.addEventListener("DOMContentLoaded", () => {
  const userIdForm = document.getElementById('user-id-form');
  const passwordForm = document.getElementById('password-form');
  const nextBtn = document.getElementById('next-btn');
  const userIdInput = document.getElementById('user-id');
  const passwordInput = document.getElementById('password');
  const welcomeMessage = document.getElementById('welcome-message');
  
  // Error message element for invalid ID or password
  const errorMessage = document.createElement('p');
  errorMessage.style.color = 'red';
  errorMessage.style.marginTop = '10px';
  errorMessage.style.display = 'none';
  passwordForm.appendChild(errorMessage);

  // List of valid User IDs with corresponding names and passwords
  const validUsers = {
    "123": { name: "Smith", password: "password123" },
    "456": { name: "Johnson", password: "password456" },
    "789": { name: "Williams", password: "password789" }
  };

  let currentUserId = '';

  // Step 1: Handle User ID Input and Move to Password Form
  nextBtn.addEventListener('click', () => {
    const userId = userIdInput.value.trim();

    if (userId in validUsers) {
      // If User ID is valid, show the password form
      const doctorName = validUsers[userId].name;
      welcomeMessage.innerHTML = `Welcome<br>Dr. ${doctorName}`;
      
      // Hide the User ID form and show the Password form
      currentUserId = userId;
      userIdForm.style.display = 'none';
      passwordForm.style.display = 'block';
      errorMessage.style.display = 'none'; // Hide any previous error message
    } else {
      // If User ID is invalid, show an error message
      errorMessage.textContent = 'Invalid ID. Please try again.';
      errorMessage.style.display = 'block';
    }
  });

  // Step 2: Verify the password when the form is submitted
  passwordForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const enteredPassword = passwordInput.value.trim();
    const correctPassword = validUsers[currentUserId].password;

    if (enteredPassword === correctPassword) {
      alert('Login successful!');
      // Here you would send the data to your backend or proceed further
    } else {
      // Show an error message if the password is incorrect
      errorMessage.textContent = 'Invalid password. Please try again.';
      errorMessage.style.display = 'block';
    }
  });
});

