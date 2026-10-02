document.addEventListener("DOMContentLoaded", function () {

    const passwordFields = document.querySelectorAll(
        "input[type='password']"
    );

    passwordFields.forEach(function (field) {

        field.addEventListener("input", function () {

            if (field.value.length < 6) {
                field.style.borderColor = "red";
            } else {
                field.style.borderColor = "";
            }

        });

    });

});