document.addEventListener("DOMContentLoaded", function () {

    const confirmElements = document.querySelectorAll(".confirm-action");

    confirmElements.forEach(function (element) {

        element.addEventListener("click", function (event) {

            const message =
                element.getAttribute("data-confirm") ||
                "Are you sure you want to continue?";

            const confirmed = window.confirm(message);

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});