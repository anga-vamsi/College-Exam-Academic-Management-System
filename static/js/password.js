document.addEventListener("DOMContentLoaded", function () {

    const passwordFields = document.querySelectorAll(
        "input[type='password']"
    );

    passwordFields.forEach(function (field) {

        const wrapper = field.parentElement;

        const button = document.createElement("button");

        button.type = "button";
        button.textContent = "Show";
        button.className = "password-toggle";

        wrapper.appendChild(button);

        button.addEventListener("click", function () {

            if (field.type === "password") {
                field.type = "text";
                button.textContent = "Hide";
            } else {
                field.type = "password";
                button.textContent = "Show";
            }

        });

    });

});