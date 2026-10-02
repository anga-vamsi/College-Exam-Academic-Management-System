document.addEventListener("DOMContentLoaded", function () {

    const tables = document.querySelectorAll("table");

    tables.forEach(function (table) {

        table.addEventListener("click", function (event) {

            const row = event.target.closest("tbody tr");

            if (!row) {
                return;
            }

            table.querySelectorAll("tbody tr").forEach(function (currentRow) {
                currentRow.classList.remove("selected-row");
            });

            row.classList.add("selected-row");

        });

    });

});