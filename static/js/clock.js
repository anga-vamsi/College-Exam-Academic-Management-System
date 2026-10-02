document.addEventListener("DOMContentLoaded", function () {

    const clock = document.querySelector(".live-clock");

    if (!clock) {
        return;
    }

    function updateClock() {

        const now = new Date();

        clock.textContent = now.toLocaleString();

    }

    updateClock();

    setInterval(updateClock, 1000);

});