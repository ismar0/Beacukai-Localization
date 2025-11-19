import frappe
import requests
from beacukai.beacukai.api.api40 import export_dokumen_pabean
from beacukai.beacukai.api.token import get_valid_ceisa_token
import json
import datetime
from frappe.utils.password import get_decrypted_password

@frappe.whitelist()
def post_dokumen_pabean(name):
    payload = export_dokumen_pabean(name)
    token = get_valid_ceisa_token()
    settings = frappe.get_single("CEISA Settings")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(
            f"{settings.api_url}/document",
            data=json.dumps(payload, default=default_converter),
            headers={**headers, "Content-Type": "application/json"}
        )
        res.raise_for_status()
        data = res.json()

        # Simpan idHeader atau response ke dokumen
        if data.get("status") == "OK":
            frappe.db.set_value("Dokumen Pabean", name, "id_header", data.get("idHeader"))
            frappe.msgprint("✅ Berhasil kirim ke CEISA.")
        else:
            frappe.throw(f"❌ Gagal kirim ke CEISA: {data}")

    except requests.exceptions.RequestException as e:
        frappe.log_error(str(e), "POST CEISA Error")
        frappe.throw("❌ Terjadi kesalahan saat mengirim ke CEISA.")

def default_converter(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")


#cetak formulir
@frappe.whitelist()
def cetak_formulir(nomor_aju):
    import requests
    settings = frappe.get_single("CEISA Settings")
    token = get_valid_ceisa_token()

    url = f"{settings.api_url}/respon/cetak-formulir"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/pdf"
    }
    params = {"nomorAju": nomor_aju}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        file_name = f"Formulir_{nomor_aju}.pdf"

        # Hapus file lama jika ada
        existing_file = frappe.db.get_value(
            "File",
            {"file_name": file_name, "attached_to_doctype": "Dokumen Pabean", "attached_to_name": nomor_aju},
            "name"
        )
        if existing_file:
            frappe.delete_doc("File", existing_file)

        # Simpan file baru
        filedoc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "is_private": 1,
            "content": response.content,
            "attached_to_doctype": "Dokumen Pabean",
            "attached_to_name": nomor_aju,
        })
        filedoc.save(ignore_permissions=True)

        return {
            "status": "success",
            "file_url": filedoc.file_url,
            "message": "File berhasil disimpan dan ditimpa jika sebelumnya sudah ada."
        }

    else:
        frappe.throw(f"Gagal cetak formulir dari CEISA: {response.status_code} - {response.text}")
