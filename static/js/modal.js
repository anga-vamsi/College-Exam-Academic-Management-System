document.addEventListener("DOMContentLoaded", function () {

    const modalButtons = document.querySelectorAll("[data-modal-target]");

    modalButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute("data-modal-target");
            const modal = document.getElementById(targetId);

            if (modal) {
                modal.classList.add("active");
            }

        });

    });

    const closeButtons = document.querySelectorAll(".modal-close");

    closeButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const modal = button.closest(".modal");

            if (modal) {
                modal.classList.remove("active");
            }

        });

    });

    document.querySelectorAll(".modal").forEach(function (modal) {

        modal.addEventListener("click", function (event) {

            if (event.target === modal) {
                modal.classList.remove("active");
            }

        });

    });

});