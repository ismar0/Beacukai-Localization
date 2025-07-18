// Copyright (c) 2025, Ismarwanto and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Dokumen Pabean", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Dokumen Pabean', {
    onload: function (frm) {
        // Set tanggal_aju ke hari ini jika belum ada
        if (frm.is_new() && !frm.doc.tanggal_aju) {
            frm.set_value("tanggal_aju", frappe.datetime.get_today());
        }

        frm.set_query('tujuan_pengiriman', function () {
            if (!frm.doc.bctype) return {};
            return {
                filters: {
                    kode_dokumen: frm.doc.bctype
                }
            };
        });
    },

    refresh: function (frm) {
        // Auto generate nomor_aju jika sudah punya bctype dan tanggal_aju tapi belum ada nomor_aju
        if (frm.doc.bctype && frm.doc.tanggal_aju && !frm.doc.nomor_aju) {
            generate_nomor_aju(frm);
        }
    },

    bctype: function (frm) {
        // Saat pilih bctype manual
        if (frm.doc.bctype && frm.doc.tanggal_aju && !frm.doc.nomor_aju) {
            generate_nomor_aju(frm);
        }
    }
});

function generate_nomor_aju(frm) {
    frappe.call({
        method: "beacukai.beacukai.doctype.header.header.generate_nomor_aju_api",
        args: {
            bctype: frm.doc.bctype,
            tanggal_aju: frm.doc.tanggal_aju
        },
        callback: function (r) {
            if (r.message) {
                frm.set_value("nomor_aju", r.message);
            }
        }
    });
}


