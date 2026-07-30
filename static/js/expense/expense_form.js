document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("expense-form");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (validateForm()) {
            form.submit();
        }
    });

    function validateForm() {
        let valid = true;

        clearErrors();

        valid = checkRequired("id_title", "title") && valid;
        valid = checkRequired("id_amount", "amount") && valid;
        valid = checkRequired("id_category", "category") && valid;
        valid = checkRequired("id_payment_method", "payment_method") && valid;
        valid = checkRequired("id_date", "date") && valid;

        return valid;
    }

    function checkRequired(inputId, fieldName) {
        const input = document.getElementById(inputId);

        if (!input || input.value.trim() === "") {
            showError(fieldName, "This field is required.");
            return false;
        }

        return true;
    }

    function showError(fieldName, message) {
        const error = document.getElementById(`${fieldName}-error`);

        if (error) {
            error.textContent = message;
        }
    }

    function clearErrors() {
        document.querySelectorAll(".js-error").forEach(error => {
            error.textContent = "";
        });
    }
});