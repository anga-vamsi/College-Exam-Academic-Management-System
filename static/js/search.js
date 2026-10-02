document.addEventListener("DOMContentLoaded", function () {

    const searchInputs = document.querySelectorAll(".table-search");

    searchInputs.forEach(function (input) {

        input.addEventListener("input", function () {

            const searchText = input.value.toLowerCase().trim();
            const tableId = input.getAttribute("data-table");
            const table = document.getElementById(tableId);

            if (!table) {
                return;
            }

            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const rowText = row.textContent.toLowerCase();

                if (rowText.includes(searchText)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    });

});