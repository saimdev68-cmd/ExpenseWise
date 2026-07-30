document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("recurring-form");

    if (!form) return;

    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton ? submitButton.textContent : 'Save';

    function clearErrors() {
        // Remove dynamically added error messages
        document.querySelectorAll(".js-error").forEach(error => {
            error.remove();
        });

        // Remove invalid class from fields
        form.querySelectorAll(".is-invalid").forEach(field => {
            field.classList.remove("is-invalid");
        });

        // Clear any non-field errors container
        const nonFieldErrors = document.getElementById("non-field-errors");
        if (nonFieldErrors) {
            nonFieldErrors.remove();
        }
    }

    function showError(field, message) {
        if (!field) return;

        field.classList.add("is-invalid");

        // Find the form group
        const formGroup = field.closest(".form-group");
        if (!formGroup) return;

        // Check if error already exists
        let error = formGroup.querySelector(".js-error");
        if (!error) {
            error = document.createElement("span");
            error.className = "field-error-msg js-error";
            formGroup.appendChild(error);
        }
        
        error.textContent = message;
    }

    function showNonFieldErrors(messages) {
        let container = document.getElementById("non-field-errors");

        if (!container) {
            container = document.createElement("div");
            container.id = "non-field-errors";
            container.className = "alert alert-danger js-error";
            container.style.cssText = `
                background-color: #fef2f2;
                border: 1px solid #fca5a5;
                color: #991b1b;
                padding: 0.75rem 1rem;
                border-radius: 0.375rem;
                margin-bottom: 1rem;
            `;
            form.prepend(container);
        }

        container.innerHTML = "";

        messages.forEach(message => {
            const div = document.createElement("div");
            div.textContent = message;
            div.style.marginBottom = "0.25rem";
            container.appendChild(div);
        });
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        clearErrors();

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Saving...";
        }

        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: new FormData(form),
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                window.location.href = data.redirect_url;
                return;
            }

            // Handle errors
            if (data.errors) {
                // Handle field-specific errors
                Object.entries(data.errors).forEach(([field, messages]) => {
                    if (field === "__all__") {
                        showNonFieldErrors(messages);
                        return;
                    }

                    const input = document.getElementById(`id_${field}`);
                    if (input) {
                        showError(input, Array.isArray(messages) ? messages.join(" ") : messages);
                    } else {
                        // If field not found, show as non-field error
                        showNonFieldErrors([`${field}: ${Array.isArray(messages) ? messages.join(" ") : messages}`]);
                    }
                });
            } else {
                // If no specific errors but response not successful
                showNonFieldErrors(["An error occurred. Please check your input and try again."]);
            }

        } catch (error) {
            console.error("Error submitting form:", error);
            showNonFieldErrors([
                "Network error. Please check your connection and try again."
            ]);
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        }
    });

    // Handle dynamic field toggling for transaction type
    const typeField = document.getElementById("id_transaction_type");
    const incomeRow = document.getElementById("income-category-row");
    const expenseRow = document.getElementById("expense-category-row");
    const paymentRow = document.getElementById("payment-method-row");

    function toggleFields() {
        if (!typeField) return;
        
        const value = typeField.value;

        if (incomeRow) {
            incomeRow.style.display = value === "INCOME" ? "flex" : "none";
        }
        if (expenseRow) {
            expenseRow.style.display = value === "EXPENSE" ? "flex" : "none";
        }
        if (paymentRow) {
            paymentRow.style.display = value === "EXPENSE" ? "flex" : "none";
        }
    }

    if (typeField) {
        toggleFields();
        typeField.addEventListener("change", toggleFields);
    }
});