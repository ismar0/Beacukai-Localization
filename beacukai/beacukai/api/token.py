from datetime import timedelta
import frappe
import requests

@frappe.whitelist()
def get_ceisa_token():
    settings = frappe.get_single("CEISA Settings")

    username = settings.ceisa_username
    password = settings.get_password("ceisa_password")
    url = settings.auth_url.strip()

    payload = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

        token = data.get("item", {}).get("access_token")
        refresh_token = data.get("item", {}).get("refresh_token")
        expires_in = data.get("item", {}).get("expires_in", 7200)  # detik

        # Simpan ke Doctype
        settings.db_set("access_token", token)
        settings.db_set("refresh_token", refresh_token)
        settings.db_set("token_expiry", frappe.utils.now_datetime() + timedelta(seconds=expires_in))

        # Simpan ke cache juga (optional)
        frappe.cache().set_value("ceisa_access_token", token)
        frappe.cache().set_value("ceisa_refresh_token", refresh_token)

        return {
            "success": True,
            "access_token": token,
            "message": "Token berhasil diperoleh"
        }

    except requests.exceptions.RequestException as e:
        error_text = res.text if 'res' in locals() else str(e)
        frappe.log_error(f"Status: {res.status_code}\nResponse: {error_text}", "CEISA Token Error")
        return {
            "success": False,
            "error": f"{res.status_code} - {error_text}"
        }

def get_valid_ceisa_token():
    settings = frappe.get_single("CEISA Settings")

    token = settings.access_token
    expiry = settings.token_expiry
    refresh_token = settings.refresh_token

    now = frappe.utils.now_datetime()

    if token and expiry and expiry > now:
        return token  # Token masih aktif

    # Kalau sudah expired, coba refresh
    return refresh_ceisa_token(refresh_token, settings)

def refresh_ceisa_token(refresh_token, settings=None):
    if not settings:
        settings = frappe.get_single("CEISA Settings")

    url = settings.auth_url.strip().replace("/user/login", "/user/refresh")  # pastikan URL refresh benar

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

        token = data.get("item", {}).get("access_token")
        new_refresh_token = data.get("item", {}).get("refresh_token")
        expires_in = data.get("item", {}).get("expires_in", 7200)

        # Simpan token baru
        settings.db_set("access_token", token)
        settings.db_set("refresh_token", new_refresh_token)
        settings.db_set("token_expiry", frappe.utils.now_datetime() + timedelta(seconds=expires_in))

        return token

    except requests.exceptions.RequestException as e:
        error_text = res.text if 'res' in locals() else str(e)
        frappe.log_error(f"Status: {res.status_code}\nResponse: {error_text}", "CEISA Refresh Token Error")
        frappe.throw("❌ Gagal refresh token CEISA. Silakan login ulang.")
