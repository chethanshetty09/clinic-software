"""
KayaSparsha - Database operations via Supabase
"""

import streamlit as st
from supabase import create_client, Client
import hashlib
import datetime


@st.cache_resource
def get_supabase() -> Client:
    """Initialize Supabase client (cached across reruns)."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# ─── Auth ────────────────────────────────────────────────────────

def authenticate_user(username: str, password: str):
    sb = get_supabase()
    result = sb.table("users").select("*").eq("username", username).eq("is_active", True).execute()
    if result.data and result.data[0]["password_hash"] == hash_password(password):
        return result.data[0]
    return None


# ─── Users ───────────────────────────────────────────────────────

def get_users():
    sb = get_supabase()
    return sb.table("users").select("*").order("created_at", desc=True).execute().data

def create_user(data: dict):
    sb = get_supabase()
    data["password_hash"] = hash_password(data.pop("password"))
    return sb.table("users").insert(data).execute()

def update_user(uid: int, data: dict):
    sb = get_supabase()
    if "password" in data:
        pwd = data.pop("password")
        if pwd:
            data["password_hash"] = hash_password(pwd)
    return sb.table("users").update(data).eq("id", uid).execute()


# ─── Patients ────────────────────────────────────────────────────

def generate_patient_uid():
    sb = get_supabase()
    result = sb.table("patients").select("id", count="exact").execute()
    count = result.count or 0
    now = datetime.datetime.now()
    return f"KS-{now.year}{now.month:02d}-{count + 1:04d}"

def get_patients(search: str = ""):
    sb = get_supabase()
    query = sb.table("patients").select("*").order("created_at", desc=True)
    if search:
        query = query.or_(f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,patient_uid.ilike.%{search}%,phone.ilike.%{search}%")
    return query.execute().data

def get_patient(pid: int):
    sb = get_supabase()
    result = sb.table("patients").select("*").eq("id", pid).execute()
    return result.data[0] if result.data else None

def create_patient(data: dict):
    sb = get_supabase()
    data["patient_uid"] = generate_patient_uid()
    result = sb.table("patients").insert(data).execute()
    return result.data[0] if result.data else None

def update_patient(pid: int, data: dict):
    sb = get_supabase()
    data["updated_at"] = datetime.datetime.now().isoformat()
    return sb.table("patients").update(data).eq("id", pid).execute()


# ─── Consultations ───────────────────────────────────────────────

def get_consultations(doctor_id: int = None):
    sb = get_supabase()
    query = sb.table("consultations").select("*, patients(first_name, last_name, patient_uid), users(full_name)").order("created_at", desc=True)
    if doctor_id:
        query = query.eq("doctor_id", doctor_id)
    return query.execute().data

def get_consultation(cid: int):
    sb = get_supabase()
    result = sb.table("consultations").select("*, patients(first_name, last_name, patient_uid, age, sex, phone, address, city), users(full_name, qualification, registration_no)").eq("id", cid).execute()
    return result.data[0] if result.data else None

def get_patient_consultations(pid: int):
    sb = get_supabase()
    return sb.table("consultations").select("*, users(full_name, qualification, registration_no)").eq("patient_id", pid).order("created_at", desc=True).execute().data

def create_consultation(data: dict):
    sb = get_supabase()
    result = sb.table("consultations").insert(data).execute()
    return result.data[0] if result.data else None

def update_consultation(cid: int, data: dict):
    sb = get_supabase()
    data["updated_at"] = datetime.datetime.now().isoformat()
    return sb.table("consultations").update(data).eq("id", cid).execute()


# ─── Follow-ups ──────────────────────────────────────────────────

def get_follow_ups(consultation_id: int):
    sb = get_supabase()
    return sb.table("follow_ups").select("*, users(full_name, qualification)").eq("consultation_id", consultation_id).order("created_at", desc=True).execute().data

def create_follow_up(data: dict):
    sb = get_supabase()
    # Also update consultation status
    sb.table("consultations").update({"status": "follow_up", "updated_at": datetime.datetime.now().isoformat()}).eq("id", data["consultation_id"]).execute()
    return sb.table("follow_ups").insert(data).execute()


# ─── Services ────────────────────────────────────────────────────

def get_services():
    sb = get_supabase()
    return sb.table("services").select("*").eq("is_active", True).order("category").order("name").execute().data

def create_service(data: dict):
    sb = get_supabase()
    return sb.table("services").insert(data).execute()

def update_service(sid: int, data: dict):
    sb = get_supabase()
    return sb.table("services").update(data).eq("id", sid).execute()

def delete_service(sid: int):
    sb = get_supabase()
    return sb.table("services").update({"is_active": False}).eq("id", sid).execute()


# ─── Invoices ────────────────────────────────────────────────────

def generate_invoice_number():
    sb = get_supabase()
    result = sb.table("invoices").select("id", count="exact").execute()
    count = result.count or 0
    now = datetime.datetime.now()
    return f"INV-{now.year}{now.month:02d}-{count + 1:04d}"

def get_invoices():
    sb = get_supabase()
    return sb.table("invoices").select("*, patients(first_name, last_name, patient_uid, phone)").order("created_at", desc=True).execute().data

def get_invoice(iid: int):
    sb = get_supabase()
    result = sb.table("invoices").select("*, patients(first_name, last_name, patient_uid, phone, address, city, email)").eq("id", iid).execute()
    inv = result.data[0] if result.data else None
    if inv:
        items = sb.table("invoice_items").select("*").eq("invoice_id", iid).execute().data
        inv["items"] = items
    return inv

def create_invoice(data: dict, items: list):
    sb = get_supabase()
    data["invoice_number"] = generate_invoice_number()
    result = sb.table("invoices").insert(data).execute()
    if result.data:
        inv_id = result.data[0]["id"]
        for item in items:
            item["invoice_id"] = inv_id
            sb.table("invoice_items").insert(item).execute()
        return result.data[0]
    return None


# ─── Dashboard ───────────────────────────────────────────────────

def get_dashboard_stats():
    sb = get_supabase()
    today = datetime.date.today().isoformat()

    total_patients = sb.table("patients").select("id", count="exact").execute().count or 0
    today_patients = sb.table("patients").select("id", count="exact").gte("created_at", f"{today}T00:00:00").execute().count or 0
    total_consults = sb.table("consultations").select("id", count="exact").execute().count or 0
    today_consults = sb.table("consultations").select("id", count="exact").gte("created_at", f"{today}T00:00:00").execute().count or 0
    pending = sb.table("consultations").select("id", count="exact").eq("status", "pending").execute().count or 0

    # Revenue
    all_invoices = sb.table("invoices").select("grand_total, created_at").eq("payment_status", "paid").execute().data
    total_revenue = sum(float(i["grand_total"]) for i in all_invoices) if all_invoices else 0
    today_revenue = sum(float(i["grand_total"]) for i in all_invoices if i["created_at"][:10] == today) if all_invoices else 0

    return {
        "total_patients": total_patients,
        "today_patients": today_patients,
        "total_consultations": total_consults,
        "today_consultations": today_consults,
        "pending": pending,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
    }


# ─── Reports ─────────────────────────────────────────────────────

def get_patients_report():
    sb = get_supabase()
    return sb.table("patients").select("patient_uid, first_name, last_name, age, sex, phone, email, address, city, state, pincode, blood_group, created_at").order("created_at", desc=True).execute().data

def get_invoices_report():
    sb = get_supabase()
    return sb.table("invoices").select("invoice_number, total_amount, discount, tax, grand_total, payment_method, payment_status, created_at, patients(patient_uid, first_name, last_name)").order("created_at", desc=True).execute().data

def get_consultations_report():
    sb = get_supabase()
    return sb.table("consultations").select("visit_type, main_complaint, diagnosis, oral_medication, panchakarma_therapy, status, created_at, patients(patient_uid, first_name, last_name), users(full_name)").order("created_at", desc=True).execute().data


# ─── Prescriptions (receptionist view) ───────────────────────────

def get_generated_prescriptions():
    sb = get_supabase()
    return sb.table("consultations").select("id, patient_id, oral_medication, panchakarma_therapy, created_at, patients(patient_uid, first_name, last_name, phone), users(full_name)").eq("prescription_generated", True).order("updated_at", desc=True).execute().data

def get_doctors():
    sb = get_supabase()
    return sb.table("users").select("id, full_name, qualification, registration_no").eq("role", "doctor").eq("is_active", True).execute().data
