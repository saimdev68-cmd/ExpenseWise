document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".auth-form");

    if (!form) {
        return;
    }


    // ---------------------------------------------------------
    // NON-FIELD ERROR CONTAINER
    // ---------------------------------------------------------

    let nonFieldErrorContainer =
        form.querySelector(".non-field-errors");

    if (!nonFieldErrorContainer) {

        nonFieldErrorContainer =
            document.createElement("ul");

        nonFieldErrorContainer.className =
            "non-field-errors";

        nonFieldErrorContainer.style.display =
            "none";

        form.insertBefore(
            nonFieldErrorContainer,
            form.firstChild
        );
    }


    // ---------------------------------------------------------
    // CLEAR ERRORS
    // ---------------------------------------------------------

    function clearErrors() {

        form.querySelectorAll(".errorlist")
            .forEach(function (element) {
                element.remove();
            });


        form.querySelectorAll(".form-control")
            .forEach(function (input) {

                input.classList.remove(
                    "is-invalid"
                );

            });


        nonFieldErrorContainer.innerHTML = "";

        nonFieldErrorContainer.style.display =
            "none";
    }


    // ---------------------------------------------------------
    // SHOW NON-FIELD ERRORS
    // ---------------------------------------------------------

    function showNonFieldErrors(errors) {

        if (!errors || errors.length === 0) {
            return;
        }


        errors.forEach(function (error) {

            const li =
                document.createElement("li");

            /*
             * Django get_json_data() returns:
             *
             * {
             *   "message": "...",
             *   "code": "..."
             * }
             */

            if (
                typeof error === "object" &&
                error.message
            ) {

                li.textContent =
                    error.message;

            } else {

                li.textContent =
                    String(error);

            }


            nonFieldErrorContainer.appendChild(li);

        });


        nonFieldErrorContainer.style.display =
            "block";
    }


    // ---------------------------------------------------------
    // SHOW FIELD ERRORS
    // ---------------------------------------------------------

    function showFieldErrors(
        fieldName,
        errors
    ) {

        const input =
            form.querySelector(
                '[name="' + fieldName + '"]'
            );


        if (!input) {
            return;
        }


        input.classList.add(
            "is-invalid"
        );


        const errorList =
            document.createElement("ul");

        errorList.className =
            "errorlist";


        errors.forEach(function (error) {

            const li =
                document.createElement("li");


            if (
                typeof error === "object" &&
                error.message
            ) {

                li.textContent =
                    error.message;

            } else {

                li.textContent =
                    String(error);

            }


            errorList.appendChild(li);

        });


        /*
         * Put the error after the input.
         */

        input.insertAdjacentElement(
            "afterend",
            errorList
        );
    }


    // ---------------------------------------------------------
    // FORM SUBMIT
    // ---------------------------------------------------------

    form.addEventListener(
        "submit",
        async function (event) {

            /*
             * VERY IMPORTANT:
             *
             * This prevents the browser's
             * normal form submission.
             */

            event.preventDefault();

            event.stopPropagation();


            clearErrors();


            const formData =
                new FormData(form);


            const csrfToken =
                form.querySelector(
                    '[name="csrfmiddlewaretoken"]'
                );


            try {

                const response =
                    await fetch(
                        form.action ||
                        window.location.href,
                        {
                            method: "POST",

                            body: formData,

                            credentials: "same-origin",

                            headers: {

                                "X-Requested-With":
                                    "XMLHttpRequest",

                                "Accept":
                                    "application/json",

                                "X-CSRFToken":
                                    csrfToken
                                        ? csrfToken.value
                                        : ""
                            }
                        }
                    );


                /*
                 * Get response as text first.
                 *
                 * This helps us debug if Django
                 * returns HTML instead of JSON.
                 */

                const responseText =
                    await response.text();


                let data;


                try {

                    data =
                        JSON.parse(
                            responseText
                        );

                } catch (jsonError) {

                    console.error(
                        "Server returned non-JSON:",
                        responseText
                    );

                    throw new Error(
                        "Server returned HTML instead of JSON."
                    );
                }


                // -------------------------------------------------
                // SUCCESS
                // -------------------------------------------------

                if (
                    response.ok &&
                    data.success
                ) {

                    /*
                     * Navigate ONLY after successful
                     * AJAX response.
                     */

                    window.location.assign(
                        data.redirect_url
                    );

                    return;
                }


                // -------------------------------------------------
                // VALIDATION ERRORS
                // -------------------------------------------------

                if (data.errors) {

                    Object.entries(
                        data.errors
                    ).forEach(
                        function (
                            [fieldName, errors]
                        ) {

                            /*
                             * Non-field errors
                             */

                            if (
                                fieldName === "__all__" ||
                                fieldName === "None"
                            ) {

                                showNonFieldErrors(
                                    errors
                                );

                                return;
                            }


                            /*
                             * Field errors
                             */

                            showFieldErrors(
                                fieldName,
                                errors
                            );

                        }
                    );
                }


            } catch (error) {

                console.error(
                    "Password reset error:",
                    error
                );


                showNonFieldErrors([
                    "Something went wrong. Please try again."
                ]);

            }

        }
    );

});