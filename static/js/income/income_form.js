document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("all-form");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const valid = validateForm();
        if (valid) {
            form.submit();
        }
    });
    function validateForm() {
        let valid = true;
        clearErrors();
        valid &= checkRequired("id_title", "title");
        valid &= checkRequired("id_amount", "amount");
        valid &= checkRequired("id_date", "date");
        valid &= checkRequired('id_category',"category")
        return Boolean(valid);
    }

    function checkRequired(inputId, fieldName) {
        const input = document.getElementById(inputId);
        if (!input.value.trim()) {
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