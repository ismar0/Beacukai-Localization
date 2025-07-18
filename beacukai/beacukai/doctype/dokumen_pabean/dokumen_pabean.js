// Copyright (c) 2025, Ismarwanto and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dokumen Pabean', {
    onload: function (frm) {
        if (frm.is_new() && !frm.doc.tanggal_aju) {
            frm.set_value("tanggal_aju", frappe.datetime.get_today());
        }

        if (
            frm.is_new() &&
            !frm.doc.tanggal_pernyataan &&
            !frm.doc.setuju &&
            !frm.doc.kota_pernyataan &&
            !frm.doc.nama_pernyataan &&
            !frm.doc.jabatan_pernyataan &&
            !frm.doc.kantor_pabean
        ) {
            get_data_pernyataan(frm);
        }

        set_vendor_doctype(frm);

    },

    refresh: function (frm) {
        // Hanya generate nomor aju jika belum diisi
        if (frm.doc.bctype && frm.doc.tanggal_aju && !frm.doc.nomor_aju) {
            generate_nomor_aju(frm);
        }

        // Jika data pernyataan masih kosong, ambil dari CEISA Settings
        if (
            !frm.doc.setuju &&
            !frm.doc.kota_pernyataan &&
            !frm.doc.nama_pernyataan &&
            !frm.doc.jabatan_pernyataan &&
            !frm.doc.tanggal_pernyataan &&
            !frm.doc.kantor_pabean
        ) {
            get_data_pernyataan(frm);
        }

        // Set seri & link Doctype
        set_seri_entitas(frm);
        set_vendor_doctype(frm);
        set_seri_dokumen(frm);
        set_seri_pengangkut(frm);
        set_seri_kemasan(frm);
        set_seri_kontainer(frm);
    },

    validate: function (frm) {
        set_seri_entitas(frm);
        set_seri_dokumen(frm);
        set_seri_pengangkut(frm);
        set_seri_kemasan(frm);
        set_seri_kontainer(frm);
    },

    bctype: function (frm) {
        if (frm.doc.bctype && frm.doc.tanggal_aju && !frm.doc.nomor_aju) {
            generate_nomor_aju(frm);
        }
        set_vendor_doctype(frm);
    }
});

function generate_nomor_aju(frm) {
    frappe.call({
        method: "beacukai.beacukai.doctype.dokumen_pabean.dokumen_pabean.generate_nomor_aju_api",
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

function get_data_pernyataan(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "CEISA Settings",
            name: "CEISA Settings"
        },
        callback: function (r) {
            if (r.message) {
                const s = r.message;
                frm.set_value("kota_pernyataan", s.kota_pernyataan);
                frm.set_value("tanggal_pernyataan", frappe.datetime.get_today());
                frm.set_value("nama_pernyataan", s.penanggung_jawab);
                frm.set_value("jabatan_pernytaan", s.jabatan);
                frm.set_value("setuju", true);
                frm.set_value("kantor_pabean", s.kppbc);
            }
        }
    });
}

function set_seri_entitas(frm) {
    let seri = 3;
    (frm.doc.table_bdwa || []).forEach(row => {
        if (row.jenis_entitas === "3") {
            row.seri_entitas = 1;
        } else if (row.jenis_entitas === "7") {
            row.seri_entitas = 2;
        } else {
            row.seri_entitas = seri++;
        }
    });
    frm.refresh_field("table_bdwa");
}

function set_seri_dokumen(frm) {
    (frm.doc.table_dmyp || []).forEach((row, idx) => {
        row.seri_dokumen = idx + 1;
    });
    frm.refresh_field("table_dmyp");
}

function set_seri_pengangkut(frm) {
    (frm.doc.table_qdlt || []).forEach((row, idx) => {
        row.seri_pengangkut = idx + 1;
    });
    frm.refresh_field("table_qdlt");
}

function set_seri_kemasan(frm) {
    (frm.doc.table_tmah || []).forEach((row, idx) => {
        row.seri_kemasan = idx + 1;
    });
    frm.refresh_field("table_tmah");
}

function set_seri_kontainer(frm) {
    (frm.doc.table_zjrd || []).forEach((row, idx) => {
        row.seri_kontainer = idx + 1;
    });
    frm.refresh_field("table_zjrd");
}

function set_vendor_doctype(frm) {
    const supplier_types = ["20", "23", "40", "262"];
    const doctype = supplier_types.includes(String(frm.doc.bctype)) ? "Supplier" : "Customer";

    (frm.doc.table_bdwa || []).forEach(row => {
        frappe.model.set_value(row.doctype, row.name, "link_doctype", doctype);
    });

    frm.fields_dict["table_bdwa"].grid.refresh();
}

frappe.ui.form.on('Entitas', {
    form_render: function (frm, cdt, cdn) {
        // Saat baris entitas dirender, set link_doctype
        const bctype = frm.doc.bctype;
        const supplier_types = ["20", "23", "40", "262"];
        const doctype = supplier_types.includes(String(bctype)) ? "Supplier" : "Customer";
        frappe.model.set_value(cdt, cdn, "link_doctype", doctype);
    },

    jenis_entitas: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Kosongkan semua field terlebih dahulu
        const fields_to_clear = [
            "nama_entitas",
            "alamat_entitas",
            "kode_jenis_identitas",
            "nomor_identitas",
            "nib",
            "no_ijin_entitas",
            "tanggal_ijin_entitas"
        ];
        fields_to_clear.forEach(field => {
            frappe.model.set_value(cdt, cdn, field, null);
        });

        if (row.jenis_entitas === "3") {
            frappe.model.set_value(cdt, cdn, "seri_entitas", 1);
        } else if (row.jenis_entitas === "7") {
            frappe.model.set_value(cdt, cdn, "seri_entitas", 2);
        }

        // Isi otomatis jika jenis_entitas adalah 3 atau 7
        if (["3", "7"].includes(row.jenis_entitas)) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "CEISA Settings",
                    name: "CEISA Settings"
                },
                callback: function (r) {
                    if (r.message) {
                        const s = r.message;
                        frappe.model.set_value(cdt, cdn, "nama_entitas", s.perusahaan);
                        frappe.model.set_value(cdt, cdn, "alamat_entitas", s.alamat);
                        frappe.model.set_value(cdt, cdn, "kode_jenis_identitas", "6");
                        frappe.model.set_value(cdt, cdn, "nomor_identitas", s.nitku);
                        frappe.model.set_value(cdt, cdn, "nib", s.nib);
                        frappe.model.set_value(cdt, cdn, "no_ijin_entitas", s.skep_no);
                        frappe.model.set_value(cdt, cdn, "tanggal_ijin_entitas", s.skep_date);
                    }
                }
            });
        }

        setTimeout(() => set_seri_entitas(frm), 300);
    },

    supplier: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const bctype = frm.doc.bctype;
        const supplier = row.supplier;

        if (!bctype || !supplier) return;

        const doctype = ["20", "23", "40", "262"].includes(String(bctype)) ? "Supplier" : "Customer";

        frappe.model.set_value(cdt, cdn, "link_doctype", doctype);

        frappe.db.get_doc(doctype, supplier).then(doc => {
            const name_field = doctype === "Supplier" ? doc.supplier_name : doc.customer_name;
            let address_field = doc.address || doc.alamat || doc.primary_address || "";

            address_field = address_field.replace(/<br\s*\/?>/gi, ' ').replace(/\s+/g, ' ').trim();

            frappe.model.set_value(cdt, cdn, "nama_entitas", name_field || supplier);
            frappe.model.set_value(cdt, cdn, "alamat_entitas", address_field);
        });
    }
});

frappe.ui.form.on('Dokumen', {
    form_render: function (frm, cdt, cdn) {
        set_seri_dokumen(frm);
    },

    table_dmyp_add: function (frm) {
        set_seri_dokumen(frm);
    },

    table_dmyp_remove: function (frm) {
        set_seri_dokumen(frm);
    }
});

frappe.ui.form.on('Pengangkut', {
    form_render: function (frm, cdt, cdn) {
        set_seri_pengangkut(frm);
    },

    table_qdlt_add: function (frm) {
        set_seri_pengangkut(frm);
    },

    table_qdlt_remove: function (frm) {
        set_seri_pengangkut(frm);
    }
});

frappe.ui.form.on('Kemasan', {
    form_render: function (frm, cdt, cdn) {
        set_seri_kemasan(frm);
    },

    table_tmah_add: function (frm) {
        set_seri_kemasan(frm);
    },

    table_tmah_remove: function (frm) {
        set_seri_kemasan(frm);
    }
});

frappe.ui.form.on('Kontainer', {
    form_render: function (frm, cdt, cdn) {
        set_seri_kontainer(frm);
    },

    table_zjrd_add: function (frm) {
        set_seri_kontainer(frm);
    },

    table_zjrd_remove: function (frm) {
        set_seri_kontainer(frm);
    }
});

frappe.ui.form.on('Barang', {
    grid_row_render: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const grid_row = frm.fields_dict.table_barang.grid.grid_rows_by_docname[cdn];

        if (!grid_row) return;

        const $row = grid_row.$row;

        // Cegah duplikasi tombol
        if ($row.find(`#tarif-container-${cdn}`).length === 0) {
            $row.append(`
                <div style="margin-top: 10px;">
                    <button class="btn btn-sm btn-primary btn-expand-tarif" data-rowname="${cdn}">Lihat Tarif</button>
                    <div id="tarif-container-${cdn}" style="margin-top: 10px; display: none;"></div>
                </div>
            `);
        }

        // Pasang event listener langsung setelah tombol dibuat
        $row.find('.btn-expand-tarif').off('click').on('click', function (e) {
            const $btn = $(this);
            const rowname = $btn.data('rowname');
            const row = locals['Barang'][rowname];
            const container = $(`#tarif-container-${rowname}`);

            if (container.is(':visible')) {
                container.slideUp();
                $btn.text('Lihat Tarif');
            } else {
                let html = `<table class="table table-bordered">
  <thead><tr><th>Kode Tarif</th><th>Tarif (%)</th></tr></thead><tbody>`;

                (row.table_sblq || []).forEach(t => {
                    html += `<tr><td>${t.kode_tarif || ''}</td><td>${t.tarif || ''}</td></tr>`;
                });

                html += '</tbody></table>';
                container.html(html).slideDown();
                $btn.text('Sembunyikan Tarif');
            }
        });
    }
});

frappe.ui.form.on('Barang Tarif', {
  tarif: function(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const barang = frm.doc.table_barang.find(b => b.seri_barang == row.seri_barang_tarif);
    if (barang && barang.harga_penyerahan) {
      const nilai_fasilitas = barang.harga_penyerahan * (row.tarif || 0) / 100;
      frappe.model.set_value(cdt, cdn, 'nilai_fasilitas', nilai_fasilitas);
    }
  }
});
