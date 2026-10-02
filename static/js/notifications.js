function showNotification(message, type) {

    const notification = document.createElement("div");

    notification.className =
        "alert alert-" + (type || "info");

    notification.textContent = message;

    document.body.prepend(notification);

    setTimeout(function () {

        notification.style.transition = "opacity 0.5s";
        notification.style.opacity = "0";

        setTimeout(function () {
            notification.remove();
        }, 500);

    }, 3000);
}