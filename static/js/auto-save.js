document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll(".auto-save");

    forms.forEach(function (form) {

        const fields = form.querySelectorAll("input, textarea, select");

        fields.forEach(function (field) {

            field.addEventListener("change", function () {

                localStorage.setItem(
                    "form_" + field.name,
                    field.value
                );

            });

        });

    });

});