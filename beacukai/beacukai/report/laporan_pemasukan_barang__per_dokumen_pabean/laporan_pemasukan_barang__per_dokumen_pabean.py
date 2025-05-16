# Copyright (c) 2025, Ismarwanto and contributors
# For license information, please see license.txt

# import frappe


import frappe

@frappe.whitelist()
def execute(filters=None):
    if isinstance(filters, str):  # ✅ Fix: Convert filters if passed as a string
        import json
        filters = json.loads(filters)

    if not filters:
        filters = {}

    columns = [
        {"fieldname": "bctype", "label": "Jenis", "fieldtype": "Data"},
        {"fieldname": "nomor_daftar", "label": "No. Daftar", "fieldtype": "Data"},
		{"fieldname": "tanggal_daftar", "label": "Tgl. Daftar", "fieldtype": "Date"},
        {"fieldname": "name", "label": "No. Trans", "fieldtype": "Data"},
		{"fieldname": "tglTrans", "label": "Tgl. Trans", "fieldtype": "Date"},
        {"fieldname": "supplier_name", "label": "Pengirim Barang", "fieldtype": "Data"},
		{"fieldname": "KdBrg", "label": "Kode Barang", "fieldtype": "Data"},
		{"fieldname": "item_name", "label": "Nama Barang", "fieldtype": "Data"},
		{"fieldname": "uom", "label": "Satuan Barang", "fieldtype": "Data"},
        {"fieldname": "received_qty", "label": "Jumlah Barang", "fieldtype": "Float"},
        # {"fieldname": "rate", "label": "Rate", "fieldtype": "Currency"},
        # {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency"}
    ]

    conditions = ["b.status != 'Cancelled'"]  # ✅ Exclude records where status is "Cancelled"
    if "from_date" in filters and filters["from_date"]:
        conditions.append(f"a.tanggal_daftar >= '{filters['from_date']}'")
    if "to_date" in filters and filters["to_date"]:
        conditions.append(f"a.tanggal_daftar <= '{filters['to_date']}'")

    conditions_query = " AND ".join(conditions)
    if conditions_query:
        conditions_query = "WHERE " + conditions_query

    data = frappe.db.sql(f"""
        SELECT
		a.bctype,
		a.nomor_daftar,
		a.tanggal_daftar,
		b.name,
		Date(b.creation) as tglTrans,
		b.supplier_name,
		c.name as KdBrg,
		c.item_name,
		c.received_qty,
		c.uom
		FROM tabHeader a 
		INNER JOIN `tabPurchase Receipt` b ON b.custom_document_beacukai = a.name
		INNER JOIN `tabPurchase Receipt Item` c ON c.parent = b.name
        {conditions_query}
        ORDER BY a.tanggal_daftar DESC
    """, as_dict=True)

    return columns, data


