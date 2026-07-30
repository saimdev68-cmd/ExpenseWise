document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("budget-form");

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        clearErrors();

        if (!validateRequired()) {
            return;
        }

        const category = document.getElementById("id_category").value;
        const month = document.getElementById("id_month").value;
        const year = document.getElementById("id_year").value;

        const budgetId = form.dataset.pk || "";

        const params = new URLSearchParams({
            category,
            month,
            year,
            budget_id: budgetId
        });

        const response = await fetch(
            `/budgets/check-budget/?${params.toString()}`,
            {
                headers:{
                    "X-Requested-With":"XMLHttpRequest"
                }
            }
        );

        const data = await response.json();

        if(data.exists){

            showError(
                "category",
                "Budget already exists for this category, month and year."
            );

            return;
        }

        form.submit();

    });

    function validateRequired(){

        let valid = true;

        valid = checkRequired("id_category","category") && valid;
        valid = checkRequired("id_amount","amount") && valid;
        valid = checkRequired("id_month","month") && valid;
        valid = checkRequired("id_year","year") && valid;

        return valid;
    }

    function checkRequired(id,name){

        const input = document.getElementById(id);

        if(!input.value){

            showError(name,"This field is required.");

            return false;
        }

        return true;
    }

    function showError(field,message){

        document.getElementById(`${field}-error`).textContent = message;
    }

    function clearErrors(){

        document.querySelectorAll(".js-error").forEach(error=>{

            error.textContent = "";

        });

    }

});