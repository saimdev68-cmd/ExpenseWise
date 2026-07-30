// AJAX Form Submission
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
        submitBtn.textContent = 'Change Password';

        if (res.status === 200 && res.body.success) {
            window.location.href = res.body.redirect_url;
        } else if (res.status === 400 && res.body.errors) {
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
                            span.style.cssText = 'display: block; margin-top: 0.25rem; color: #ef4444; font-size: 0.825rem; font-weight: 500;';
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
        submitBtn.textContent = 'Change Password';
        console.error('Submission error:', error);
    });
});