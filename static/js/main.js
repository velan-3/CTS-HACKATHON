document.addEventListener('DOMContentLoaded', () => {
    const doctorIdForm = document.getElementById('doctor-id-form');
    const doctorPasswordForm = document.getElementById('doctor-password-form');
    const doctorWelcomeMessage = document.getElementById('doctor-welcome-message');  // Get the welcome message element
    let currentUserId = null;
    let currentDoctorName = null;  // Store the doctor's name

    // Handle Doctor ID submission
    document.getElementById('doctor-next-btn').addEventListener('click', async () => {
        const doctorId = document.getElementById('doctor-id').value.trim();
        try {
            const response = await fetch('/verify_id', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: doctorId, userType: 'doctor' })
            });

            const data = await response.json();
            if (data.success) {
                currentUserId = doctorId;
                currentDoctorName = data.name;  // Get doctor's name from the response

                // Update the password form title with the doctor's name
                doctorWelcomeMessage.textContent = `Welcome Dr. ${currentDoctorName}`;

                // Show password form and hide the ID form
                doctorIdForm.style.display = 'none';
                doctorPasswordForm.style.display = 'block';
            } else {
                document.getElementById('doctor-id-error-message').textContent = data.message;
                document.getElementById('doctor-id-error-message').style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Handle Doctor Password submission
    document.getElementById('doctor-pass-btn').addEventListener('click', async () => {
        const password = document.getElementById('doctor-password').value.trim();
        try {
            const response = await fetch('/verify_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: currentUserId, password, userType: "doctor" })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                document.getElementById('doctor-password-error-message').textContent = data.message;
                document.getElementById('doctor-password-error-message').style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
