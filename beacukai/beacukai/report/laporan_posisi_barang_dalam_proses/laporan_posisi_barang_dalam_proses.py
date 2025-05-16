# Copyright (c) 2025, Ismarwanto and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def execute(filters=None):
    if isinstance(filters, str):  # ✅ Convert filters if passed as a string
        import json
        filters = json.loads(filters)

    if not filters:
        filters = {}

    # Define Report Columns
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data"},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data"},
        {"fieldname": "uom", "label": "Unit of Measure", "fieldtype": "Data"},
        {"fieldname": "qty", "label": "Quantity", "fieldtype": "Float"},
        {"fieldname": "remarks", "label": "Remarks", "fieldtype": "Data"}
    ]

    # Apply Filters (Date & Warehouse)
    conditions = ["sle.docstatus = 1", "sle.warehouse = 'Work In Progress - ST'"]  # ✅ Filter WIP Store only

    if "from_date" in filters and filters["from_date"]:
        conditions.append(f"sle.posting_date >= '{filters['from_date']}'")
    if "to_date" in filters and filters["to_date"]:
        conditions.append(f"sle.posting_date <= '{filters['to_date']}'")

    conditions_query = " AND ".join(conditions)
    if conditions_query:
        conditions_query = "WHERE " + conditions_query

    # Fetch Stock Data with Selected Date & WIP Store
    data = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            i.item_name,
            sle.stock_uom AS uom,
            SUM(sle.actual_qty) AS qty,
            "" AS remarks
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabItem` i ON sle.item_code = i.name
        {conditions_query}
        GROUP BY sle.item_code, sle.stock_uom, remarks
        ORDER BY sle.item_code
    """, as_dict=True)

    return columns, data
