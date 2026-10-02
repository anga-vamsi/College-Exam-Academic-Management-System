function printReport() {
    window.print();
}

document.addEventListener("DOMContentLoaded", function () {

    const printButtons = document.querySelectorAll(".print-report");

    printButtons.forEach(function (button) {

        button.addEventListener("click", function () {
            printReport();
        });

    });

});