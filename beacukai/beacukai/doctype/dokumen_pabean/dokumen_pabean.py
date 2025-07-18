import frappe
import json
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class DokumenPabean(Document):
    def autoname(self):
        self.name = self.nomor_aju = generate_nomor_aju(self, increment=True)

    # def validate(self):
    #     # Tambahkan entitas default jika belum ada
    #     if not self.table_bdwa:
    #         tambah_entitas_otomatis(self)
    #     self.set_seri_dokumen()
    #     self.set_seri_pengangkut()
    

    # def set_seri_dokumen(self):
    #     for i, row in enumerate(self.table_dmyp, start=1):
    #         row.seri_dokumen = i

    # def set_seri_pengangkut(self):
    #     for i, row in enumerate(self.table_qdlt, start=1):
    #         row.seri_pengangkut = i

@frappe.whitelist()
def generate_nomor_aju(doc, increment=False):
    settings = frappe.get_single("CEISA Settings")
    abbr = settings.abbr or ""
    bctype = (doc.get("bctype") or "40").zfill(4)
    bctype_final = f"{abbr}{bctype}"
    kppbc = (settings.kppbc or "071300").zfill(6)
    tanggal = getdate(doc.get("tanggal_aju") or nowdate())
    tanggal_str = tanggal.strftime("%Y%m%d")
    tahun_str = tanggal.strftime("%Y")

    counter_prefix = f"{bctype_final}{kppbc}{tahun_str}"
    nomor_aju_prefix = f"{bctype_final}{kppbc}{tanggal_str}"


    frappe.db.begin()

    settings.reload()
    counter_map = {}
    if settings.nomor_aju_counter:
        try:
            counter_map = json.loads(settings.nomor_aju_counter)
        except json.JSONDecodeError:
            pass

    current_count = counter_map.get(counter_prefix, 0)
    max_try = 10

    while max_try > 0:
        next_number = current_count + 1
        calon_nomor = f"{nomor_aju_prefix}{str(next_number).zfill(6)}"
        if not frappe.db.exists("Dokumen Pabean", calon_nomor):
            break
        current_count += 1
        max_try -= 1

    if increment:
        counter_map[counter_prefix] = next_number
        settings.nomor_aju_counter = json.dumps(counter_map, indent=2)
        settings.save(ignore_permissions=True)

    frappe.db.commit()

    return calon_nomor

@frappe.whitelist()
def generate_nomor_aju_api(bctype, tanggal_aju):
    dummy_doc = frappe._dict({
        "bctype": bctype,
        "tanggal_aju": getdate(tanggal_aju)
    })
    return generate_nomor_aju(dummy_doc)

# def tambah_entitas_otomatis(doc):
#     settings = frappe.get_single("CEISA Settings")
#     jenis_entitas_list = ["3", "7"]
#     seri = 1

#     for kode in jenis_entitas_list:
#         ent = doc.append("table_bdwa", {})  # fieldname dari child Entitas
#         ent.jenis_entitas = kode
#         ent.seri_entitas = seri
#         ent.nama_entitas = settings.perusahaan
#         ent.alamat_entitas = settings.alamat
#         ent.nomor_identitas = settings.nitku
#         ent.nib = settings.nib
#         ent.no_ijin_entitas = settings.skep_no
#         ent.tanggal_ijin_entitas = settings.skep_date
#         seri += 1
