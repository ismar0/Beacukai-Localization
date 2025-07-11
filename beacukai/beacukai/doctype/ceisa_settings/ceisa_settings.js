// Copyright (c) 2025, Ismarwanto and contributors
// For license information, please see license.txt

// frappe.ui.form.on("CEISA Settings", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("CEISA Settings", {
    refresh: function (frm) {
        frm.add_custom_button("Test Connection", function () {
            frappe.call({
                method: "beacukai.beacukai.api.token.get_ceisa_token",
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint("✅ Token berhasil diperoleh:\n" + r.message.access_token);
                        console.log("Token CEISA:", r.message.access_token);
                    } else {
                        let err_msg = (r.message && r.message.error) ? r.message.error : "Unknown error or no response";
                        frappe.msgprint("❌ Gagal mendapatkan token:\n" + err_msg);
                        console.error("CEISA Token Error:", err_msg);
                    }
                }
            });

        });
    }
});

