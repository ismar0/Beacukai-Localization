// Copyright (c) 2025, Ismarwanto and contributors
// For license information, please see license.txt

// ✅ Load Tabulator first
frappe.require([
    "https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js",
    "https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.70/pdfmake.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.70/vfs_fonts.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.7.0/jspdf.plugin.autotable.min.js"
], function() {
    console.log("✅ Tabulator and dependencies loaded!");
});


frappe.query_reports["Item Sales Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ],

    onload: function(report) {
        let reportWrapper = document.querySelector(".report-wrapper");
        if (reportWrapper) {
            reportWrapper.style.display = "block"; // Ensure report is always visible
        }
    
        setTimeout(() => {
            let tableHolder = document.querySelector(".tabulator-tableholder");
            if (tableHolder) {
                tableHolder.style.height = "auto";
                tableHolder.style.minHeight = "300px";
            }
        }, 500); // Delay to ensure Tabulator loads before fixing height
    
        getReportData();
    
        // 🔹 Listen for filter changes
        frappe.query_report.refresh = function() {
            console.log("🔄 Filters changed! Refreshing report...");
            getReportData();
        };
    }    
};

// ✅ Extract filters properly in ERPNext 15
function getFilterValues() {
    let filters = {};
    frappe.query_report.filters.forEach(filter => {
        filters[filter.df.fieldname] = filter.get_value();
    });
    console.log("🔍 Filters Extracted:", filters);
    return filters;
}

// ✅ Get report data with proper filter handling
function getReportData() {
    let filters = getFilterValues();

    frappe.call({
        method: "beacukai.beacukai.report.item_sales_report.item_sales_report.execute",
        args: { filters: filters },
        callback: function(response) {
            let data = response.message[1];

            if (!tabulatorInstance) {
                console.warn("⚠️ Tabulator not found, initializing...");
                loadTabulatorTable(data || []); // Initialize if missing
            }

            if (!data || data.length === 0) {
                console.warn("⚠️ No data received! Clearing table...");
                tabulatorInstance.clearData(); // ✅ Clear old data
                return;
            }

            console.log("✅ Data Loaded!", data);
            tabulatorInstance.replaceData(data); // ✅ Replace with new data
        }
    });
}

// ✅ Load Tabulator properly
let tabulatorInstance; // Global variable to hold Tabulator instance

function loadTabulatorTable(data = []) {
    let tableWrapper = document.getElementById("tabulator-table");

    if (!tableWrapper) {
        let reportWrapper = document.querySelector(".report-wrapper");
        if (!reportWrapper) {
            console.error("❌ Report wrapper not found!");
            return;
        }

        let tableDiv = document.createElement("div");
        tableDiv.id = "tabulator-table";
        reportWrapper.appendChild(tableDiv);
    }

    if (!tabulatorInstance) {
        tabulatorInstance = new Tabulator("#tabulator-table", {
            layout: "fitColumns",
            columns: [
                {
                    title: "Transaction",
                    columns: [
                        { title: "Invoice", field: "invoice", formatter: "link", formatterParams: function (cell) { let invoiceNumber = cell.getValue(); return { url: `/app/sales-invoice/${invoiceNumber}`, target: "_blank" }; }, width: 150 },
                        { title: "Date", field: "posting_date", sorter: "date", width: 120 }
                    ]
                },
                { title: "Customer", field: "customer", width: 150 },
                {
                    title: "Item Details",
                    columns: [
                        { title: "Item Code", field: "item_code", width: 120 },
                        { title: "Item Name", field: "item_name", width: 200 },
                        { title: "Quantity", field: "qty", sorter: "number", width: 100 }
                    ]
                },
                {
                    title: "Pricing",
                    columns: [
                        { title: "Rate", field: "rate", formatter: "money", align: "right", width: 120 },
                        { title: "Amount", field: "amount", formatter: "money", align: "right", width: 150 }
                    ]
                }
            ]
        });
    }

    tabulatorInstance.setData(data);

    // ✅ Add Export Buttons
    let exportWrapper = document.getElementById("export-buttons");
    if (!exportWrapper) {
        exportWrapper = document.createElement("div");
        exportWrapper.id = "export-buttons";
        document.querySelector(".report-wrapper").prepend(exportWrapper);

        let exportExcelBtn = document.createElement("button");
        exportExcelBtn.innerText = "📊 Export to Excel";
        exportExcelBtn.onclick = () => tabulatorInstance.download("xlsx", "Item Sales Report.xlsx");
        exportWrapper.appendChild(exportExcelBtn);

        let exportPdfBtn = document.createElement("button");
        exportPdfBtn.innerText = "📄 Export to PDF";
        exportPdfBtn.onclick = () => tabulatorInstance.download("pdf", "Item Sales Report.pdf", { orientation: "landscape", title: "Item Sales Report" });
        exportWrapper.appendChild(exportPdfBtn);
    }
}

// ✅ Refresh report when filters change
frappe.query_report.refresh = function() {
    console.log("🔄 Refreshing Report...");
    getReportData();
};
