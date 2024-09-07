document.addEventListener('DOMContentLoaded', () => {
    const authorityChoice = document.getElementById('authority-choice');
    const doctorIdForm = document.getElementById('doctor-id-form');
    const adminIdForm = document.getElementById('admin-id-form');
    const doctorPasswordForm = document.getElementById('doctor-password-form');
    const adminPasswordForm = document.getElementById('admin-password-form');

    let currentUserId = null;
    let currentUserType = null;

    // Show appropriate form based on user type
    document.getElementById('doctor-login-btn').addEventListener('click', () => {
        authorityChoice.style.display = 'none';
        doctorIdForm.style.display = 'block';
        currentUserType = 'doctor';
    });

    document.getElementById('admin-login-btn').addEventListener('click', () => {
        authorityChoice.style.display = 'none';
        adminIdForm.style.display = 'block';
        currentUserType = 'admin';
    });

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

    // Handle Admin ID submission
    document.getElementById('admin-next-btn').addEventListener('click', async () => {
        const adminId = document.getElementById('admin-id').value.trim();
        try {
            const response = await fetch('/verify_id', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: adminId, userType: 'admin' })
            });

            const data = await response.json();
            if (data.success) {
                currentUserId = adminId;
                adminIdForm.style.display = 'none';
                adminPasswordForm.style.display = 'block';
            } else {
                document.getElementById('admin-id-error-message').textContent = data.message;
                document.getElementById('admin-id-error-message').style.display = 'block';
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
                body: JSON.stringify({ userId: currentUserId, password, userType: currentUserType })
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

    // Handle Admin Password submission
    document.getElementById('admin-pass-btn').addEventListener('click', async () => {
        const password = document.getElementById('admin-password').value.trim();
        try {
            const response = await fetch('/verify_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: currentUserId, password, userType: currentUserType })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                document.getElementById('admin-password-error-message').textContent = data.message;
                document.getElementById('admin-password-error-message').style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
