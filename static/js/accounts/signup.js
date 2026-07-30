document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".auth-form");

    if (!form) {
        return;
    }

    /*
    |--------------------------------------------------------------------------
    | Non-field error container
    |--------------------------------------------------------------------------
    */

    let nonFieldErrors = form.querySelector(".non-field-errors");

    if (!nonFieldErrors) {
        nonFieldErrors = document.createElement("ul");
        nonFieldErrors.className = "non-field-errors";
        nonFieldErrors.style.display = "none";

        form.insertBefore(nonFieldErrors, form.firstChild);
    }

    /*
    |--------------------------------------------------------------------------
    | Clear all previous errors
    |--------------------------------------------------------------------------
    */

    function clearErrors() {
        // Remove field error lists
        form.querySelectorAll(".errorlist").forEach(function (element) {
            element.remove();
        });

        // Remove invalid classes
        form.querySelectorAll(".form-control").forEach(function (input) {
            input.classList.remove("is-invalid");
        });

        // Clear non-field errors
        nonFieldErrors.innerHTML = "";
        nonFieldErrors.style.display = "none";
    }

    /*
    |--------------------------------------------------------------------------
    | Create error list
    |--------------------------------------------------------------------------
    */

    function createErrorList(errors) {
        const errorList = document.createElement("ul");

        errorList.className = "errorlist";

        errors.forEach(function (error) {
            const li = document.createElement("li");

            li.textContent = error;

            errorList.appendChild(li);
        });

        return errorList;
    }

    /*
    |--------------------------------------------------------------------------
    | Show non-field errors
    |--------------------------------------------------------------------------
    */

    function showNonFieldErrors(errors) {
        if (!errors || errors.length === 0) {
            return;
        }

        errors.forEach(function (error) {
            const li = document.createElement("li");

            li.textContent = error;

            nonFieldErrors.appendChild(li);
        });

        nonFieldErrors.style.display = "block";
    }

    /*
    |--------------------------------------------------------------------------
    | Show field errors
    |--------------------------------------------------------------------------
    */

    function showFieldErrors(fieldName, errors) {
        const input = form.querySelector(
            '[name="' + fieldName + '"]'
        );

        if (!input) {
            return;
        }

        /*
        |--------------------------------------------------------------------------
        | Mark input as invalid
        |--------------------------------------------------------------------------
        */

        input.classList.add("is-invalid");

        /*
        |--------------------------------------------------------------------------
        | Create error list
        |--------------------------------------------------------------------------
        */

        const errorList = createErrorList(errors);

        /*
        |--------------------------------------------------------------------------
        | Password fields
        |--------------------------------------------------------------------------
        |
        | Structure:
        |
        | .password-field-wrapper
        |     ├── input
        |     └── toggle icon
        |
        | Error should be AFTER the wrapper.
        |
        */

        const passwordWrapper = input.closest(
            ".password-field-wrapper"
        );

        if (passwordWrapper) {
            passwordWrapper.insertAdjacentElement(
                "afterend",
                errorList
            );

            return;
        }

        /*
        |--------------------------------------------------------------------------
        | Normal fields
        |--------------------------------------------------------------------------
        */

        input.insertAdjacentElement(
            "afterend",
            errorList
        );
    }

    /*
    |--------------------------------------------------------------------------
    | Submit form
    |--------------------------------------------------------------------------
    */

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        clearErrors();

        const submitButton = form.querySelector(
            'button[type="submit"]'
        );

        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            const formData = new FormData(form);

            const csrfToken = form.querySelector(
                '[name="csrfmiddlewaretoken"]'
            );

            const response = await fetch(
                window.location.href,
                {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",

                        "X-CSRFToken": csrfToken
                            ? csrfToken.value
                            : ""
                    }
                }
            );

            /*
            |--------------------------------------------------------------------------
            | Parse response
            |--------------------------------------------------------------------------
            */

            const data = await response.json();

            /*
            |--------------------------------------------------------------------------
            | Successful registration
            |--------------------------------------------------------------------------
            */

            if (response.ok && data.success) {
                window.location.href = data.redirect_url;
                return;
            }

            /*
            |--------------------------------------------------------------------------
            | Validation errors
            |--------------------------------------------------------------------------
            */

            if (data.errors) {
                Object.keys(data.errors).forEach(function (fieldName) {
                    const errors = data.errors[fieldName];

                    /*
                    |--------------------------------------------------------------------------
                    | Django non-field errors
                    |--------------------------------------------------------------------------
                    */

                    if (
                        fieldName === "__all__" ||
                        fieldName === "None"
                    ) {
                        showNonFieldErrors(errors);
                        return;
                    }

                    /*
                    |--------------------------------------------------------------------------
                    | Field errors
                    |--------------------------------------------------------------------------
                    */

                    showFieldErrors(
                        fieldName,
                        errors
                    );
                });
            }

        } catch (error) {
            console.error(
                "Registration error:",
                error
            );

            showNonFieldErrors([
                "Something went wrong. Please try again."
            ]);

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });

    /*
    |--------------------------------------------------------------------------
    | Remove error when user starts typing
    |--------------------------------------------------------------------------
    */

    form.addEventListener("input", function (event) {
        const input = event.target;

        if (!input.classList.contains("form-control")) {
            return;
        }

        /*
        |--------------------------------------------------------------------------
        | Remove invalid state
        |--------------------------------------------------------------------------
        */

        input.classList.remove("is-invalid");

        /*
        |--------------------------------------------------------------------------
        | Password field
        |--------------------------------------------------------------------------
        */

        const passwordWrapper = input.closest(
            ".password-field-wrapper"
        );

        if (passwordWrapper) {
            const nextElement =
                passwordWrapper.nextElementSibling;

            if (
                nextElement &&
                nextElement.classList.contains("errorlist")
            ) {
                nextElement.remove();
            }

            return;
        }

        /*
        |--------------------------------------------------------------------------
        | Normal field
        |--------------------------------------------------------------------------
        */

        const nextElement = input.nextElementSibling;

        if (
            nextElement &&
            nextElement.classList.contains("errorlist")
        ) {
            nextElement.remove();
        }
    });
});

