document.addEventListener("DOMContentLoaded", function () {

    const resetButtons = document.querySelectorAll(".reset-form");

    resetButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const form = button.closest("form");

            if (form) {
                form.reset();
            }

        });

    });

});