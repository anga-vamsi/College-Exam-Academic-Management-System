function exportTableToCSV(tableId, filename) {

    const table = document.getElementById(tableId);

    if (!table) {
        return;
    }

    const rows = table.querySelectorAll("tr");
    const csv = [];

    rows.forEach(function (row) {

        const cells = row.querySelectorAll("th, td");

        const rowData = [];

        cells.forEach(function (cell) {
            const value = cell.textContent
                .trim()
                .replace(/"/g, '""');

            rowData.push('"' + value + '"');
        });

        csv.push(rowData.join(","));

    });

    const blob = new Blob(
        [csv.join("\n")],
        { type: "text/csv;charset=utf-8;" }
    );

    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = filename || "report.csv";

    link.click();

    URL.revokeObjectURL(link.href);
}