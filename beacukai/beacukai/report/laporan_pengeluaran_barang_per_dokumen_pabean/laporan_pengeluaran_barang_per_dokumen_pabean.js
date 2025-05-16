// Copyright (c) 2025, Ismarwanto and contributors
// For license information, please see license.txt

// ✅ Load Tabulator and dependencies
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

frappe.query_reports["LAPORAN PENGELUARAN BARANG PER DOKUMEN PABEAN"] = {
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
            reportWrapper.style.display = "block";  
            reportWrapper.style.padding = "10px";
            reportWrapper.style.backgroundColor = "#f8f9fa";
            reportWrapper.style.borderRadius = "8px";
        }
    
        setTimeout(() => {
            let tableHolder = document.querySelector(".tabulator-tableholder");
            if (tableHolder) {
                tableHolder.style.height = "auto";
                tableHolder.style.minHeight = "300px";
                tableHolder.style.overflowX = "auto";
            }

            // ✅ Streamline column filters
            document.querySelectorAll(".tabulator-header-filter input").forEach(input => {
                input.style.width = "100%";
                input.style.height = "24px";
                input.style.padding = "4px";
                input.style.fontSize = "12px";
                input.style.border = "1px solid #ccc";
                input.style.borderRadius = "4px";
                input.style.boxSizing = "border-box";
            });

        }, 500); 
    
        getReportData();
    
        frappe.query_report.refresh = function() {
            console.log("🔄 Filters changed! Refreshing report...");
            getReportData();
        };
    }    
};

// ✅ Extract filters properly
function getFilterValues() {
    let filters = {};
    frappe.query_report.filters.forEach(filter => {
        filters[filter.df.fieldname] = filter.get_value();
    });
    console.log("🔍 Filters Extracted:", filters);
    return filters;
}

// ✅ Get report data
function getReportData() {
    
    let filters = getFilterValues();

    frappe.call({
        method: "beacukai.beacukai.report.laporan_pengeluaran_barang_per_dokumen_pabean.laporan_pengeluaran_barang_per_dokumen_pabean.execute",
        args: { filters: filters },
        callback: function(response) {
            let data = response.message[1];

            if (!tabulatorInstance) {
                console.warn("⚠️ Tabulator not found, initializing...");
                loadTabulatorTable(data || []); 
            }

            if (!data || data.length === 0) {
                console.warn("⚠️ No data received! Clearing table...");
                tabulatorInstance.clearData(); 
                return;
            }

            console.log("✅ Data Loaded!", data);
            tabulatorInstance.replaceData(data);
        }
    });
}

// ✅ Load Tabulator properly
let tabulatorInstance; 

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
                    title: "Data Dok Pabean",
                    columns: [
                        { title: "Jenis", field: "bctype", width: 100, headerFilter: "input" },
                        { title: "No. Daftar", field: "nomor_daftar", width: 120, headerFilter: "input" },
                        { title: "Tgl. Daftar", field: "tanggal_daftar", sorter: "date", width: 120, headerFilter: "input" }
                    ]
                },
                {
                    title: "Bukti Pengeluaran Barang",
                    columns: [
                        { title: "No", field: "name", widthGrow: 1.5, headerFilter: "input" },
                        { title: "Tanggal", field: "tglTrans", sorter: "date", width: 120, headerFilter: "input" }
                    ]
                },
                {
                    title: "",
                    columns: [
                        { title: "Penerima Barang", field: "customer_name", width: 120, headerFilter: "input" },
                        { title: "Kode Barang", field: "KdBrg", width: 120, headerFilter: "input" },
                        { title: "Nama Barang", field: "item_name", width: 120, headerFilter: "input" },
                        { title: "Satuan Barang", field: "uom", width: 100, headerFilter: "input" },
                        { title: "Jumlah Barang", field: "qty", sorter: "number", width: 100, headerFilter: "input"},
                    ]
                },
            ],
            headerFilterLiveFilterDelay: 300, // Prevents lag when typing
            headerFilterLiveFilter: false // Prevents continuous filtering as you type
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
        exportExcelBtn.onclick = () => tabulatorInstance.download("xlsx", "laporan_pengeluaran_barang.xlsx");
        exportWrapper.appendChild(exportExcelBtn);

        let exportPdfBtn = document.createElement("button");
        exportPdfBtn.innerText = "📄 Export to PDF";
        exportPdfBtn.onclick = () => tabulatorInstance.download("pdf", "laporan_pengeluaran_barang.pdf", { orientation: "landscape", title: "LAPORAN PENGELUARAN BARANG PER DOKUMEN PABEAN" });
        exportWrapper.appendChild(exportPdfBtn);

        // ✅ Style export buttons
        document.querySelectorAll("#export-buttons button").forEach(button => {
            button.style.margin = "5px";
            button.style.padding = "6px 12px";
            button.style.fontSize = "14px";
            button.style.cursor = "pointer";
            button.style.border = "none";
            button.style.borderRadius = "4px";
            button.style.backgroundColor = "#007bff";
            button.style.color = "#fff";
            button.onmouseover = () => button.style.backgroundColor = "#0056b3";
            button.onmouseout = () => button.style.backgroundColor = "#007bff";
        });
    }
}

// ✅ Refresh report when filters change
frappe.query_report.refresh = function() {
    console.log("🔄 Refreshing Report...");
    getReportData();
};

