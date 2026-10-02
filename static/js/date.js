document.addEventListener("DOMContentLoaded", function () {

    const dateFields = document.querySelectorAll(
        "input[type='date']"
    );

    dateFields.forEach(function (field) {

        field.addEventListener("change", function () {

            if (field.value) {
                field.classList.add("has-value");
            } else {
                field.classList.remove("has-value");
            }

        });

    });

});