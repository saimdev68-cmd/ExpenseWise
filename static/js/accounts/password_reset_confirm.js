document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".auth-form");
    if (!form) return;

    // Handle non-field error container initialization (hidden by default)
    let nonFieldErrorContainer = form.querySelector(".non-field-errors");
    if (!nonFieldErrorContainer) {
        nonFieldErrorContainer = document.createElement("ul");
        nonFieldErrorContainer.className = "non-field-errors";
        nonFieldErrorContainer.style.display = "none";
        form.insertBefore(nonFieldErrorContainer, form.firstChild);
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        
        // Reset error states and hide container
        nonFieldErrorContainer.innerHTML = "";
        nonFieldErrorContainer.style.display = "none";
        nonFieldErrorContainer.classList.remove("error", "success");
        document.querySelectorAll(".errorlist").forEach(el => el.remove());
        document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));

        const formData = new FormData(form);

        fetch(window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            if (status === 200 && body.success) {
                window.location.href = body.redirect_url;
            } else if (body.errors) {
                let hasNonFieldErrors = false;
                
                for (const [field, errors] of Object.entries(body.errors)) {
                    if (field === "__all__" || field === "None") {
                        errors.forEach(err => {
                            if (err && err.trim() !== "") {
                                const li = document.createElement("li");
                                li.textContent = err;
                                nonFieldErrorContainer.appendChild(li);
                                hasNonFieldErrors = true;
                            }
                        });
                    } else {
                        const inputField = form.querySelector(`[name="${field}"]`);
                        if (inputField) {
                            inputField.classList.add("is-invalid");
                            
                            const errorUl = document.createElement("ul");
                            errorUl.className = "errorlist";
                            errors.forEach(err => {
                                const li = document.createElement("li");
                                li.textContent = err;
                                errorUl.appendChild(li);
                            });

                            // Handle password wrappers cleanly if fields are wrapped
                            const wrapper = inputField.closest(".password-field-wrapper");
                            if (wrapper) {
                                wrapper.after(errorUl);
                            } else {
                                inputField.parentNode.appendChild(errorUl);
                            }
                        }
                    }
                }
                
                if (hasNonFieldErrors) {
                    nonFieldErrorContainer.classList.add("error");
                    nonFieldErrorContainer.style.display = "block";
                }
            }
        })
        .catch(error => {
            console.error("Password reset confirmation error:", error);
        });
    });
});