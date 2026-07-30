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
    submitBtn.textContent = 'Processing...';

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
        submitBtn.textContent = 'Edit Email';

        if (res.status === 200 && res.body.success) {
            // Success: Move to OTP verify page without reload interruption
            window.location.href = res.body.redirect_url;
        } else if (res.status === 400 && res.body.errors) {
            // Validation/Service Error: Inject error messages dynamically
            const errors = res.body.errors;
            
            for (const [fieldName, errorList] of Object.entries(errors)) {
                if (fieldName === '__all__') {
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
        submitBtn.textContent = 'Send OTP & Update';
        console.error('Submission error:', error);
    });
});
