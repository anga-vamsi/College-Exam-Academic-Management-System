document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            document.querySelectorAll(".modal.active").forEach(function (modal) {
                modal.classList.remove("active");
            });

        }

    });

});