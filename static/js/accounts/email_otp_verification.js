document.getElementById('ajax-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const form = this;
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submit-btn');
    
    // Clear old errors
    document.querySelectorAll('.field-error-msg').forEach(el => el.remove());
    const nonFieldErrorsList = document.getElementById('non-field-errors');
    nonFieldErrorsList.innerHTML = '';
    nonFieldErrorsList.style.display = 'none';

    submitBtn.disabled = true;
    submitBtn.textContent = 'Verifying...';

    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(res => {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Verify Code';

        if (res.status === 200 && res.body.success) {
            // Success: Head to user_detail profile page without reloading context
            window.location.href = res.body.redirect_url;
        } else if (res.status === 400 && res.body.errors) {
            // Error: Parse and inject validation errors dynamically
            const errors = res.body.errors;
            
            for (const [fieldName, errorList] of Object.entries(errors)) {
                if (fieldName === '__all__' || fieldName === 'None' || !fieldName) {
                    nonFieldErrorsList.style.display = 'block';
                    errorList.forEach(err => {
                        const li = document.createElement('li');
                        li.textContent = err;
                        nonFieldErrorsList.appendChild(li);
                    });
                } else {
                    const fieldGroup = form.querySelector(`[data-field="${fieldName}"]`);
                    if (fieldGroup) {
                        const errorContainer = fieldGroup.querySelector('.field-errors-container');
                        errorList.forEach(err => {
                            const span = document.createElement('span');
                            span.className = 'field-error-msg';
                            span.textContent = err;
                            errorContainer.appendChild(span);
                        });
                    }
                }
            }
        }
    })
    .catch(error => {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Verify Code';
        console.error('Submission error:', error);
    });
});
document.getElementById('resend-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const form = this;
    const formData = new FormData(form);
    const resendBtn = document.getElementById('resend-btn');
    
    resendBtn.disabled = true;
    resendBtn.textContent = 'Sending...';

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(res => {
        resendBtn.disabled = false;
        resendBtn.textContent = '🔄 Resend OTP';

        // Create or select a message display container dynamically
        let msgContainer = document.getElementById('ajax-message-container');
        if (!msgContainer) {
            msgContainer = document.createElement('div');
            msgContainer.id = 'ajax-message-container';
            msgContainer.style.cssText = 'margin-bottom: 1rem; padding: 0.75rem 1rem; border-radius: 4px; font-size: 0.9rem;';
            form.parentNode.insertBefore(msgContainer, form);
        }

        if (res.status === 200 && res.body.success) {
            // Style as success message
            msgContainer.style.backgroundColor = '#d4edda';
            msgContainer.style.color = '#155724';
            msgContainer.style.border = '1px solid #c3e6cb';
            msgContainer.textContent = res.body.message;

            if (res.body.redirect_url) {
                setTimeout(() => {
                    window.location.href = res.body.redirect_url;
                }, 1500); // Wait 1.5 seconds so user can read the success message before reload/redirect
            }
        } else {
            // Style as error message
            msgContainer.style.backgroundColor = '#f8d7da';
            msgContainer.style.color = '#721c24';
            msgContainer.style.border = '1px solid #f5c6cb';
            msgContainer.textContent = res.body.message || 'Failed to resend code.';
        }
    })
    .catch(error => {
        resendBtn.disabled = false;
        resendBtn.textContent = '🔄 Resend OTP';
        console.error('Resend error:', error);
    });
});