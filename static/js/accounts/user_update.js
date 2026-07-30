document.getElementById('ajax-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const form = this;
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submit-btn');
    
    // Clear previous error styles/messages
    document.querySelectorAll('.field-error-msg').forEach(el => el.remove());
    const nonFieldErrorsList = document.getElementById('non-field-errors');
    nonFieldErrorsList.innerHTML = '';
    nonFieldErrorsList.style.display = 'none';

    submitBtn.disabled = true;
    submitBtn.textContent = 'Updating...';

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
        submitBtn.textContent = 'Update Name';

        if (res.status === 200 && res.body.success) {
            // Success: Redirect to success_url
            window.location.href = res.body.redirect_url;
        } else if (res.status === 400 && res.body.errors) {
            // Validation Error: Render errors dynamically without reload
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
        submitBtn.textContent = 'Update Name';
        console.error('Submission error:', error);
    });
});