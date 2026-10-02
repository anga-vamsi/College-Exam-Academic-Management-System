document.addEventListener("DOMContentLoaded", function () {

    function updateTableClass() {

        const tables = document.querySelectorAll("table");

        tables.forEach(function (table) {

            if (table.scrollWidth > table.clientWidth) {
                table.classList.add("wide-table");
            } else {
                table.classList.remove("wide-table");
            }

        });

    }

    updateTableClass();

    window.addEventListener("resize", updateTableClass);

});