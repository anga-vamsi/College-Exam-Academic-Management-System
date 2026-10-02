document.addEventListener("DOMContentLoaded", function () {

    const numberFields = document.querySelectorAll(
        "input[type='number']"
    );

    numberFields.forEach(function (field) {

        field.addEventListener("input", function () {

            const min = field.getAttribute("min");
            const max = field.getAttribute("max");

            if (min !== null && Number(field.value) < Number(min)) {
                field.value = min;
            }

            if (max !== null && Number(field.value) > Number(max)) {
                field.value = max;
            }

        });

    });

});