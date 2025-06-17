# Copyright (c) 2025, Ismarwanto and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.utils import getdate

@frappe.whitelist()
def execute(filters=None):
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    # Filter hanya gudang tertentu
    warehouse_list = ["Scrap & Reject - AAM"]

    columns = [
        {"fieldname": "item_code", "label": "Kode Barang", "fieldtype": "Data"},
        {"fieldname": "item_name", "label": "Nama Barang", "fieldtype": "Data"},
        {"fieldname": "uom", "label": "Satuan", "fieldtype": "Data"},
        {"fieldname": "saldo_awal", "label": "Saldo Awal", "fieldtype": "Float"},
        {"fieldname": "nilai_saldo_awal", "label": "Nilai Saldo Awal", "fieldtype": "Currency"},
        {"fieldname": "pemasukan", "label": "Pemasukan", "fieldtype": "Float"},
        {"fieldname": "nilai_pemasukan", "label": "Nilai Pemasukan", "fieldtype": "Currency"},
        {"fieldname": "pengeluaran", "label": "Pengeluaran", "fieldtype": "Float"},
        {"fieldname": "nilai_pengeluaran", "label": "Nilai Pengeluaran", "fieldtype": "Currency"},
        {"fieldname": "adjustment", "label": "Adjustment", "fieldtype": "Float"},
        {"fieldname": "saldo_akhir", "label": "Saldo Akhir", "fieldtype": "Float"},
        {"fieldname": "nilai_saldo_akhir", "label": "Nilai Saldo Akhir", "fieldtype": "Currency"},
        {"fieldname": "hasil_pencacahan", "label": "Hasil Pencacahan", "fieldtype": "Float"},
        {"fieldname": "jumlah_selisih", "label": "Jumlah Selisih", "fieldtype": "Float"},
        {"fieldname": "remarks", "label": "Keterangan", "fieldtype": "Data"},
    ]

    data_map = {}

    # Stock Ledger Entry
    sle_list = frappe.db.sql("""
        SELECT item_code, stock_uom, posting_date, voucher_type, actual_qty,
               qty_after_transaction, stock_value
        FROM `tabStock Ledger Entry`
        WHERE docstatus = 1 AND is_cancelled = 0 AND posting_date <= %s
        AND warehouse IN %s
    """, (to_date, tuple(warehouse_list)), as_dict=True)

    for sle in sle_list:
        key = sle.item_code
        if key not in data_map:
            data_map[key] = {
                "item_code": key,
                "uom": sle.stock_uom,
                "saldo_awal": 0,
                "nilai_saldo_awal": 0,
                "pemasukan": 0,
                "nilai_pemasukan": 0,
                "pengeluaran": 0,
                "nilai_pengeluaran": 0,
                "adjustment": 0,
                "hasil_pencacahan": 0
            }

        actual_qty = sle.actual_qty or 0
        stock_value = sle.stock_value or 0

        if sle.voucher_type == "Stock Reconciliation" and not actual_qty:
            actual_qty = sle.qty_after_transaction or 0

        if sle.posting_date < from_date:
            data_map[key]["saldo_awal"] += flt(actual_qty)
            data_map[key]["nilai_saldo_awal"] += flt(stock_value)
        elif from_date <= sle.posting_date <= to_date:
            if actual_qty > 0:
                data_map[key]["pemasukan"] += flt(actual_qty)
                data_map[key]["nilai_pemasukan"] += flt(stock_value)
            elif actual_qty < 0:
                data_map[key]["pengeluaran"] += abs(flt(actual_qty))
                data_map[key]["nilai_pengeluaran"] += flt(stock_value)

    # Stock Reconciliation
    adj = frappe.db.sql("""
        SELECT sri.item_code, SUM(sri.qty) AS adjustment
        FROM `tabStock Reconciliation Item` sri
        INNER JOIN `tabStock Reconciliation` sr ON sri.parent = sr.name
        WHERE sr.docstatus = 1 AND sr.purpose = 'Stock Reconciliation'
        AND sr.posting_date BETWEEN %s AND %s
        AND sri.warehouse IN %s
        GROUP BY sri.item_code
    """, (from_date, to_date, tuple(warehouse_list)), as_dict=True)

    for row in adj:
        key = row.item_code
        if key not in data_map:
            data_map[key] = {
                "item_code": key,
                "uom": "",
                "saldo_awal": 0,
                "nilai_saldo_awal": 0,
                "pemasukan": 0,
                "nilai_pemasukan": 0,
                "pengeluaran": 0,
                "nilai_pengeluaran": 0,
                "adjustment": 0,
                "hasil_pencacahan": 0
            }
        data_map[key]["adjustment"] = flt(row.adjustment)

    # Stock Entry Scrap
    scrap = frappe.db.sql("""
        SELECT sei.item_code, SUM(sei.qty) AS hasil
        FROM `tabStock Entry Detail` sei
        INNER JOIN `tabStock Entry` se ON sei.parent = se.name
        WHERE se.docstatus = 1 AND se.stock_entry_type = 'Scrap'
        AND se.posting_date BETWEEN %s AND %s
        AND sei.t_warehouse IN %s
        GROUP BY sei.item_code
    """, (from_date, to_date, tuple(warehouse_list)), as_dict=True)

    for row in scrap:
        key = row.item_code
        if key not in data_map:
            data_map[key] = {
                "item_code": key,
                "uom": "",
                "saldo_awal": 0,
                "nilai_saldo_awal": 0,
                "pemasukan": 0,
                "nilai_pemasukan": 0,
                "pengeluaran": 0,
                "nilai_pengeluaran": 0,
                "adjustment": 0,
                "hasil_pencacahan": 0
            }
        data_map[key]["hasil_pencacahan"] = flt(row.hasil)

    # Final Processing
    final_data = []
    for item_code, row in data_map.items():
        item_name = frappe.db.get_value("Item", item_code, "item_name") or ""
        saldo_akhir = row["saldo_awal"] + row["pemasukan"] - row["pengeluaran"] + row["adjustment"]
        nilai_saldo_akhir = row["nilai_saldo_awal"] + row["nilai_pemasukan"] - row["nilai_pengeluaran"]
        jumlah_selisih = saldo_akhir - row["hasil_pencacahan"]

        final_data.append({
            "item_code": item_code,
            "item_name": item_name,
            "uom": row["uom"],
            "saldo_awal": row["saldo_awal"],
            "nilai_saldo_awal": row["nilai_saldo_awal"],
            "pemasukan": row["pemasukan"],
            "nilai_pemasukan": row["nilai_pemasukan"],
            "pengeluaran": row["pengeluaran"],
            "nilai_pengeluaran": row["nilai_pengeluaran"],
            "adjustment": row["adjustment"],
            "saldo_akhir": saldo_akhir,
            "nilai_saldo_akhir": nilai_saldo_akhir,
            "hasil_pencacahan": row["hasil_pencacahan"],
            "jumlah_selisih": jumlah_selisih,
            "remarks": ""
        })

    return columns, final_data
