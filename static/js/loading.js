document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const loading = document.querySelector(".loading");

            if (loading) {
                loading.classList.add("active");
            }

        });

    });

});