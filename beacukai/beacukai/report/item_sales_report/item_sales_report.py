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
        {"fieldname": "invoice", "label": "Invoice", "fieldtype": "Link", "options": "Sales Invoice"},
        {"fieldname": "posting_date", "label": "Date", "fieldtype": "Date"},
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Data"},
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data"},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data"},
        {"fieldname": "qty", "label": "Quantity", "fieldtype": "Float"},
        {"fieldname": "rate", "label": "Rate", "fieldtype": "Currency"},
        {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency"}
    ]

    conditions = []
    if "from_date" in filters and filters["from_date"]:
        conditions.append(f"si.posting_date >= '{filters['from_date']}'")
    if "to_date" in filters and filters["to_date"]:
        conditions.append(f"si.posting_date <= '{filters['to_date']}'")

    conditions_query = " AND ".join(conditions)
    if conditions_query:
        conditions_query = "WHERE " + conditions_query

    data = frappe.db.sql(f"""
        SELECT 
            si.name as invoice,
            si.posting_date,
            si.customer,
            sii.item_code,
            sii.item_name,
            sii.qty,
            sii.rate,
            sii.amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        {conditions_query}
        ORDER BY si.posting_date DESC
    """, as_dict=True)

    return columns, data


