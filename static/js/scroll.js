document.addEventListener("DOMContentLoaded", function () {

    const scrollButton = document.querySelector(".scroll-top");

    if (!scrollButton) {
        return;
    }

    window.addEventListener("scroll", function () {

        if (window.scrollY > 300) {
            scrollButton.classList.add("active");
        } else {
            scrollButton.classList.remove("active");
        }

    });

    scrollButton.addEventListener("click", function () {

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    });

});