document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const requiredFields = form.querySelectorAll("[required]");
            let valid = true;

            requiredFields.forEach(function (field) {

                if (field.value.trim() === "") {
                    field.style.borderColor = "red";
                    valid = false;
                } else {
                    field.style.borderColor = "";
                }

            });

            if (!valid) {
                event.preventDefault();
                alert("Please fill in all required fields.");
                return;
            }

            // Allow the normal Flask form submission.
            // Do not call preventDefault() when the form is valid.
        });

    });

});