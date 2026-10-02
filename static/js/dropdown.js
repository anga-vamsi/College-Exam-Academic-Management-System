document.addEventListener("DOMContentLoaded", function () {

    const dropdownButtons = document.querySelectorAll(".dropdown-toggle");

    dropdownButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const dropdown = button.parentElement;

            dropdown.classList.toggle("active");

        });

    });

});