document.addEventListener("DOMContentLoaded", function () {

    const cards = document.querySelectorAll(".card");

    cards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {
            card.style.transform = "translateY(-3px)";
        });

        card.addEventListener("mouseleave", function () {
            card.style.transform = "";
        });

    });

});