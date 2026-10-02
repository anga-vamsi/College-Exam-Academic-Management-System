document.addEventListener("DOMContentLoaded", function () {

    const profileForm = document.querySelector("#profile-form");

    if (!profileForm) {
        return;
    }

    profileForm.addEventListener("submit", function () {

        const button = profileForm.querySelector("button[type='submit']");

        if (button) {
            button.disabled = true;
            button.textContent = "Saving...";
        }

    });

});