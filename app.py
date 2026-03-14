"""
🌿 KayaSparsha - Ayurvedic Clinic Management System
Streamlit + Supabase
"""

import streamlit as st
import pandas as pd
import datetime
import io
import os
import base64
import urllib.parse
import db

# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="KayaSparsha - Ayurvedic Clinic",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  LOGO HELPER
# ═══════════════════════════════════════════════════════════════════

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

@st.cache_data
def get_logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def logo_img_tag(width=180):
    b64 = get_logo_base64()
    if b64:
        return f'<img src="data:image/png;base64,{b64}" width="{width}" style="display:block; margin:0 auto;" />'
    return '<h2 style="color:#2D5016; margin:0; font-family:Playfair Display,serif;">KayaSparsha</h2>'

def show_logo_centered(width=200):
    if os.path.exists(LOGO_PATH):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image(LOGO_PATH, width=width)
    else:
        st.markdown("<div style='text-align:center;font-size:56px'>🌿</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;font-family:Playfair Display,serif;color:#2D5016'>KayaSparsha</h1>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800&display=swap');
    .stApp { background-color: #FAF7F2; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #2D5016 0%, #1a3a0a 100%); }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] label { color: #ffffff !important; }
    .stat-card { background:white; border-radius:12px; padding:20px 24px; border:1px solid #E5E0D8; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
    .stat-value { font-family:'Playfair Display',serif; font-size:28px; font-weight:800; color:#1A1A1A; margin:0; }
    .stat-label { font-size:13px; color:#6B705C; font-weight:500; margin:0; }
    .page-title { font-family:'Playfair Display',serif; font-size:28px; font-weight:800; color:#1A1A1A; margin-bottom:4px; }
    .page-subtitle { font-size:14px; color:#6B705C; margin-bottom:24px; }
    .rx-header { text-align:center; border-bottom:3px double #2D5016; padding-bottom:16px; margin-bottom:20px; }
    .rx-header h2 { color:#2D5016; margin:0; font-family:'Playfair Display',serif; }
    .rx-header p { color:#6B705C; font-size:13px; margin:4px 0 0; }
    .rx-section { padding:8px 0; border-bottom:1px solid #E5E0D8; }
    .rx-footer { margin-top:30px; text-align:right; border-top:1px solid #ccc; padding-top:16px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton > button { border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "dashboard"
    st.session_state.selected_patient_id = None
    st.session_state.selected_consultation_id = None
    st.session_state.selected_invoice_id = None


# ═══════════════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════════════

def login_page():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("")
        show_logo_centered(220)
        st.markdown("<p style='text-align:center; color:#6B705C; margin-bottom:30px'>Clinic Management System</p>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True, type="primary"):
                user = db.authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        st.info("**Default Admin:** admin / admin123")


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════

def render_sidebar():
    user = st.session_state.user
    role = user["role"]
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=160)
        else:
            st.markdown("## 🌿 KayaSparsha")
        st.markdown("*Ayurveda for Everyday Skin*")
        st.markdown("---")
        nav = {
            "receptionist": {"📊 Dashboard": "dashboard", "👥 Patients": "patients", "📋 Prescriptions": "prescriptions", "🧾 Invoices": "invoices"},
            "doctor": {"📊 Dashboard": "dashboard", "👥 Patients": "patients", "🩺 Consultations": "consultations", "🧾 Invoices": "invoices"},
            "super_admin": {"📊 Dashboard": "dashboard", "👥 Patients": "patients", "🩺 Consultations": "consultations", "📋 Prescriptions": "prescriptions", "🧾 Invoices": "invoices", "⚕️ Services": "services", "👤 Users": "users", "📈 Reports": "reports"},
        }
        for label, key in nav.get(role, {}).items():
            if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.session_state.selected_patient_id = None
                st.session_state.selected_consultation_id = None
                st.rerun()
        st.markdown("---")
        st.markdown(f"**{user['full_name']}**")
        st.markdown(f"*{role.replace('_', ' ').title()}*")
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════

def dashboard_page():
    user = st.session_state.user
    role = user["role"]
    st.markdown(f"<div class='page-title'>Welcome, {user['full_name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>{datetime.date.today().strftime('%A, %B %d, %Y')}</div>", unsafe_allow_html=True)
    stats = db.get_dashboard_stats()

    # Top stat cards - different for each role
    if role == "receptionist":
        # Receptionist: NO revenue info
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-card'><p class='stat-label'>👥 Total Patients</p><p class='stat-value'>{stats['total_patients']}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><p class='stat-label'>🩺 Today's Consultations</p><p class='stat-value'>{stats['today_consultations']}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><p class='stat-label'>⏳ Pending</p><p class='stat-value'>{stats['pending']}</p></div>", unsafe_allow_html=True)

    elif role == "super_admin":
        # Super Admin: Full income breakdown
        invoices_data = db.get_income_analytics()
        now = datetime.date.today()

        # Calculate monthly and annual income
        monthly_income = 0
        annual_income = 0
        week_income = 0
        week_start = now - datetime.timedelta(days=now.weekday())

        for inv in (invoices_data or []):
            amt = float(inv["grand_total"])
            inv_date = inv["created_at"][:10]
            inv_year = int(inv_date[:4])
            inv_month = int(inv_date[5:7])

            if inv_year == now.year:
                annual_income += amt
                if inv_month == now.month:
                    monthly_income += amt

            try:
                inv_dt = datetime.date.fromisoformat(inv_date)
                if inv_dt >= week_start:
                    week_income += amt
            except:
                pass

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='stat-card'><p class='stat-label'>👥 Total Patients</p><p class='stat-value'>{stats['total_patients']}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><p class='stat-label'>🩺 Today's Consultations</p><p class='stat-value'>{stats['today_consultations']}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><p class='stat-label'>⏳ Pending</p><p class='stat-value'>{stats['pending']}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat-card'><p class='stat-label'>💰 Today's Revenue</p><p class='stat-value'>₹{stats['today_revenue']:,.0f}</p></div>", unsafe_allow_html=True)

        st.markdown("")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-card'><p class='stat-label'>📅 This Week</p><p class='stat-value'>₹{week_income:,.0f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><p class='stat-label'>📆 This Month ({now.strftime('%B')})</p><p class='stat-value'>₹{monthly_income:,.0f}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><p class='stat-label'>📊 This Year ({now.year})</p><p class='stat-value'>₹{annual_income:,.0f}</p></div>", unsafe_allow_html=True)

    else:
        # Doctor: basic stats with today's revenue
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='stat-card'><p class='stat-label'>👥 Total Patients</p><p class='stat-value'>{stats['total_patients']}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><p class='stat-label'>🩺 Today's Consultations</p><p class='stat-value'>{stats['today_consultations']}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><p class='stat-label'>⏳ Pending</p><p class='stat-value'>{stats['pending']}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat-card'><p class='stat-label'>💰 Today's Revenue</p><p class='stat-value'>₹{stats['today_revenue']:,.0f}</p></div>", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recent Patients")
        patients = db.get_patients()[:8]
        if patients:
            df = pd.DataFrame(patients)[["patient_uid","first_name","last_name","age","sex","phone","created_at"]]
            df.columns = ["UID","First Name","Last Name","Age","Sex","Phone","Registered"]
            df["Registered"] = df["Registered"].str[:10]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No patients yet")
    with col2:
        st.subheader("Recent Consultations")
        consults = db.get_consultations()[:8]
        if consults:
            rows = [{"Patient": f"{c['patients']['first_name']} {c['patients']['last_name']}", "Doctor": c["users"]["full_name"], "Status": c["status"], "Date": c["created_at"][:10]} for c in consults]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("No consultations yet")


# ═══════════════════════════════════════════════════════════════════
#  PATIENTS
# ═══════════════════════════════════════════════════════════════════

def patients_page():
    user = st.session_state.user; can_register = user["role"] in ("receptionist","super_admin")
    st.markdown("<div class='page-title'>Patients</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    search = c1.text_input("🔍 Search by name, UID, or phone", key="ps")
    with c2:
        st.markdown(""); st.markdown("")
        if can_register and st.button("➕ Register Patient", type="primary", use_container_width=True):
            st.session_state.page = "register_patient"; st.rerun()
    patients = db.get_patients(search)
    if not patients: st.info("No patients found."); return
    for p in patients:
        c1,c2,c3,c4,c5 = st.columns([1.2,2,1,1.5,1])
        c1.markdown(f"**`{p['patient_uid']}`**"); c2.write(f"{p['first_name']} {p['last_name']}"); c3.write(f"{p.get('age','—')} / {p['sex']}"); c4.write(p["phone"])
        if c5.button("View", key=f"vp_{p['id']}", use_container_width=True):
            st.session_state.selected_patient_id = p["id"]; st.session_state.page = "patient_detail"; st.rerun()
        st.divider()

def register_patient_page():
    st.markdown("<div class='page-title'>Register New Patient</div>", unsafe_allow_html=True)
    if st.button("← Back to Patients"): st.session_state.page = "patients"; st.rerun()
    with st.form("rp"):
        c1,c2 = st.columns(2)
        with c1:
            first_name=st.text_input("First Name *"); dob=st.date_input("Date of Birth",value=None,min_value=datetime.date(1920,1,1)); sex=st.selectbox("Sex *",["Male","Female","Other"]); email=st.text_input("Email"); blood_group=st.selectbox("Blood Group",["","A+","A-","B+","B-","AB+","AB-","O+","O-"]); emergency_contact=st.text_input("Emergency Contact Name")
        with c2:
            last_name=st.text_input("Last Name *"); age=st.number_input("Age",0,150,0); phone=st.text_input("Phone *"); address=st.text_input("Address"); cc1,cc2=st.columns(2); city_val=cc1.text_input("City"); state_val=cc2.text_input("State"); pincode=st.text_input("Pincode"); emergency_phone=st.text_input("Emergency Phone")
        notes=st.text_area("Notes")
        if st.form_submit_button("Register Patient", type="primary", use_container_width=True):
            if not first_name or not last_name or not phone: st.error("Please fill: First Name, Last Name, Phone")
            else:
                result = db.create_patient({"first_name":first_name,"last_name":last_name,"date_of_birth":dob.isoformat() if dob else "","age":age,"sex":sex,"phone":phone,"email":email,"address":address,"city":city_val,"state":state_val,"pincode":pincode,"blood_group":blood_group,"emergency_contact":emergency_contact,"emergency_phone":emergency_phone,"notes":notes,"registered_by":st.session_state.user["id"]})
                if result: st.success(f"✅ Patient registered! **UID: {result['patient_uid']}**"); st.balloons()

def patient_detail_page():
    pid = st.session_state.selected_patient_id
    if not pid: st.session_state.page = "patients"; st.rerun(); return
    user = st.session_state.user; is_doctor = user["role"] in ("doctor","super_admin"); patient = db.get_patient(pid)
    if not patient: st.error("Patient not found"); return
    if st.button("← Back to Patients"): st.session_state.page = "patients"; st.rerun()
    st.markdown(f"### {patient['first_name']} {patient['last_name']}  `{patient['patient_uid']}`")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Age / Sex", f"{patient['age']} / {patient['sex']}"); c2.metric("Phone", patient["phone"]); c3.metric("Blood Group", patient.get("blood_group") or "—"); c4.metric("City", patient.get("city") or "—")
    st.divider()
    if not is_doctor: st.warning("🔒 Medical history is restricted to doctors and administrators only."); return
    _,col2 = st.columns([3,1])
    with col2:
        if st.button("➕ New Consultation", type="primary", use_container_width=True): st.session_state.page = "new_consultation"; st.rerun()
    st.subheader("Consultation History")
    consultations = db.get_patient_consultations(pid)
    if not consultations: st.info("No consultations yet."); return
    for c in consultations:
        doctor = c.get("users",{})
        with st.expander(f"{'🟢' if c['status']=='completed' else '🟡'} {c['visit_type'].upper()} — {c['created_at'][:10]} — Dr. {doctor.get('full_name','—')}", expanded=False):
            col1,col2 = st.columns(2)
            with col1: st.markdown(f"**Complaint:** {c.get('main_complaint') or '—'}"); st.markdown(f"**Previous History:** {c.get('previous_medical_history') or '—'}"); st.markdown(f"**Family History:** {c.get('family_history') or '—'}"); st.markdown(f"**Current Medication:** {c.get('current_medication') or '—'}")
            with col2: st.markdown(f"**Examination:** {c.get('examination') or '—'}"); st.markdown(f"**Diagnosis:** {c.get('diagnosis') or '—'}"); st.markdown(f"**℞ Oral Medication:** {c.get('oral_medication') or '—'}"); st.markdown(f"**Panchakarma:** {c.get('panchakarma_therapy') or '—'}")
            bc1,bc2,_ = st.columns(3)
            with bc1:
                if st.button("📋 Generate Prescription", key=f"rx_{c['id']}", use_container_width=True):
                    db.update_consultation(c["id"],{"prescription_generated":True}); st.session_state.selected_consultation_id=c["id"]; st.session_state.page="view_prescription"; st.rerun()
            with bc2:
                if st.button("➕ Add Follow-up", key=f"fu_{c['id']}", use_container_width=True):
                    st.session_state.selected_consultation_id=c["id"]; st.session_state.page="add_follow_up"; st.rerun()
            follow_ups = db.get_follow_ups(c["id"])
            if follow_ups:
                st.markdown("---"); st.markdown("**Follow-ups:**")
                for fu in follow_ups:
                    doc=fu.get("users",{})
                    st.markdown(f"📌 **{fu['created_at'][:10]}** — Dr. {doc.get('full_name','—')}  \nComplaint: {fu.get('follow_up_complaint') or '—'} | Medication: {fu.get('follow_up_oral_medication') or '—'} | Panchakarma: {fu.get('follow_up_panchakarma') or '—'}")


# ═══════════════════════════════════════════════════════════════════
#  CONSULTATION FORMS
# ═══════════════════════════════════════════════════════════════════

def new_consultation_page():
    pid = st.session_state.selected_patient_id; patient = db.get_patient(pid)
    if not patient: st.error("Patient not found"); return
    st.markdown("<div class='page-title'>New Consultation</div>", unsafe_allow_html=True)
    st.markdown(f"**Patient:** {patient['first_name']} {patient['last_name']} (`{patient['patient_uid']}`)")
    if st.button("← Back to Patient"): st.session_state.page = "patient_detail"; st.rerun()
    with st.form("cf"):
        mc=st.text_area("Main Complaint *",height=80); c1,c2=st.columns(2)
        with c1: ph=st.text_area("Previous Medical History",height=80); cm=st.text_area("Current Medication",height=80)
        with c2: fh=st.text_area("Family History",height=80); ex=st.text_area("Examination",height=80)
        dx=st.text_area("Diagnosis *",height=80); c1,c2=st.columns(2)
        with c1: om=st.text_area("℞ Oral Medication",height=100)
        with c2:
            # Panchakarma dropdown from services
            pk_services = db.get_panchakarma_services()
            pk_options = ["None"] + [f"{s['name']} (₹{s['price']})" for s in pk_services]
            pk_selected = st.multiselect("Panchakarma Therapy", pk_options[1:], help="Select one or more therapies from the services list")
            pk_additional = st.text_input("Additional therapy notes (optional)")
            pk_value = ", ".join(pk_selected)
            if pk_additional:
                pk_value = f"{pk_value}. {pk_additional}" if pk_value else pk_additional
        an=st.text_area("Additional Notes",height=60)
        if st.form_submit_button("💾 Save Consultation", type="primary", use_container_width=True):
            if not mc or not dx: st.error("Please fill Complaint and Diagnosis")
            else:
                db.create_consultation({"patient_id":pid,"doctor_id":st.session_state.user["id"],"visit_type":"initial","main_complaint":mc,"previous_medical_history":ph,"family_history":fh,"current_medication":cm,"examination":ex,"diagnosis":dx,"oral_medication":om,"panchakarma_therapy":pk_value,"additional_notes":an,"status":"completed"})
                st.success("✅ Consultation saved!"); st.session_state.page="patient_detail"; st.rerun()

def add_follow_up_page():
    cid=st.session_state.selected_consultation_id
    st.markdown("<div class='page-title'>Add Follow-up</div>", unsafe_allow_html=True)
    if st.button("← Back"): st.session_state.page="patient_detail"; st.rerun()
    with st.form("fuf"):
        cp=st.text_area("Follow-up Complaint",height=80); ex=st.text_area("Examination",height=80); dx=st.text_area("Diagnosis",height=80)
        c1,c2=st.columns(2)
        with c1: om=st.text_area("Oral Medication",height=100)
        with c2:
            pk_services = db.get_panchakarma_services()
            pk_selected = st.multiselect("Panchakarma Therapy", [f"{s['name']} (₹{s['price']})" for s in pk_services], key="fu_pk", help="Select therapies from the services list")
            pk_additional = st.text_input("Additional therapy notes", key="fu_pk_notes")
            pk_value = ", ".join(pk_selected)
            if pk_additional:
                pk_value = f"{pk_value}. {pk_additional}" if pk_value else pk_additional
        nt=st.text_area("Notes",height=60)
        if st.form_submit_button("💾 Save Follow-up", type="primary", use_container_width=True):
            db.create_follow_up({"consultation_id":cid,"doctor_id":st.session_state.user["id"],"follow_up_complaint":cp,"follow_up_examination":ex,"follow_up_diagnosis":dx,"follow_up_oral_medication":om,"follow_up_panchakarma":pk_value,"follow_up_notes":nt})
            st.success("✅ Follow-up saved!"); st.session_state.page="patient_detail"; st.rerun()

def consultations_page():
    st.markdown("<div class='page-title'>Consultations</div>", unsafe_allow_html=True)
    user=st.session_state.user; did=user["id"] if user["role"]=="doctor" else None; consults=db.get_consultations(did)
    if not consults: st.info("No consultations yet"); return
    rows=[{"Patient UID":c["patients"]["patient_uid"],"Patient":f"{c['patients']['first_name']} {c['patients']['last_name']}","Doctor":c["users"]["full_name"],"Type":c["visit_type"],"Complaint":(c.get("main_complaint") or "")[:60],"Status":c["status"],"Date":c["created_at"][:10]} for c in consults]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  PRESCRIPTION VIEW (with KayaSparsha logo)
# ═══════════════════════════════════════════════════════════════════

def view_prescription_page():
    cid=st.session_state.selected_consultation_id; rx=db.get_consultation(cid)
    if not rx: st.error("Not found"); return
    patient=rx.get("patients",{}); doctor=rx.get("users",{})
    if st.button("← Back"): st.session_state.page="patient_detail"; st.rerun()
    follow_ups=db.get_follow_ups(cid)
    logo_html=logo_img_tag(160)

    # Build follow-up HTML
    fu_html=""
    if follow_ups:
        fu_html="<div style='margin-top:16px;border-top:2px dashed #E5E0D8;padding-top:16px;'><h4 style='color:#B8860B;'>Follow-up Notes</h4>"
        for fu in follow_ups:
            doc=fu.get("users",{})
            fu_html+=f"<div style='background:#FFF8E7;padding:12px;border-radius:8px;margin-bottom:8px;font-size:13px;'><strong>{fu['created_at'][:10]}</strong> — Dr. {doc.get('full_name','—')}"
            if fu.get("follow_up_complaint"): fu_html+=f"<br/>Complaint: {fu['follow_up_complaint']}"
            if fu.get("follow_up_oral_medication"): fu_html+=f"<br/>Medication: {fu['follow_up_oral_medication']}"
            if fu.get("follow_up_panchakarma"): fu_html+=f"<br/>Panchakarma: {fu['follow_up_panchakarma']}"
            fu_html+="</div>"
        fu_html+="</div>"

    # Doctor info
    dr_name = doctor.get('full_name','')
    dr_qual = doctor.get('qualification','')
    dr_reg = doctor.get('registration_no','')

    # Patient info
    p_name = f"{patient.get('first_name','')} {patient.get('last_name','')}"
    p_uid = patient.get('patient_uid','')
    p_age_sex = f"{patient.get('age','')} / {patient.get('sex','')}"
    phone = patient.get("phone","")

    # Display prescription
    rx_html = f"""
    <div id="printable-rx" style="border:2px solid #2D5016;border-radius:12px;padding:24px;background:white;max-width:700px;">
        <div style="text-align:center;border-bottom:3px double #2D5016;padding-bottom:16px;margin-bottom:20px;">
            {logo_html}
            <p style="color:#6B705C;font-size:13px;margin:4px 0 0;">Ayurveda for Everyday Skin</p>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:16px;">
            <div><strong>Patient:</strong> {p_name}<br/><strong>UID:</strong> {p_uid}<br/><strong>Age/Sex:</strong> {p_age_sex}</div>
            <div style="text-align:right"><strong>Date:</strong> {rx['created_at'][:10]}<br/><strong>Doctor:</strong> Dr. {dr_name}<br/><strong>Qualification:</strong> {dr_qual}<br/><strong>Reg No:</strong> {dr_reg}</div>
        </div>
        <div style="padding:8px 0;border-bottom:1px solid #E5E0D8;"><strong>Complaint:</strong> {rx.get('main_complaint','—')}</div>
        <div style="padding:8px 0;border-bottom:1px solid #E5E0D8;"><strong>Diagnosis:</strong> {rx.get('diagnosis','—')}</div>
        {"<div style='padding:8px 0;border-bottom:1px solid #E5E0D8;'><strong>Examination:</strong> "+rx['examination']+"</div>" if rx.get('examination') else ""}
        <div style="margin-top:16px"><span style="font-size:28px;color:#2D5016;font-weight:bold;">&#8478;</span></div>
        <div style="padding:8px 0;border-bottom:1px solid #E5E0D8;"><strong style="color:#2D5016;">Oral Medication:</strong><br/><pre style="font-family:inherit;white-space:pre-wrap;margin:4px 0;">{rx.get('oral_medication','—')}</pre></div>
        <div style="padding:8px 0;border-bottom:1px solid #E5E0D8;"><strong style="color:#2D5016;">Panchakarma Therapy:</strong><br/><pre style="font-family:inherit;white-space:pre-wrap;margin:4px 0;">{rx.get('panchakarma_therapy','—')}</pre></div>
        {fu_html}
        <div style="margin-top:30px;text-align:right;border-top:1px solid #ccc;padding-top:16px;">
            <strong>Dr. {dr_name}</strong><br/>{dr_qual}<br/>Reg. No: {dr_reg}
        </div>
    </div>"""
    st.markdown(rx_html, unsafe_allow_html=True)

    # Print button - opens new window with ONLY the prescription
    print_html = rx_html.replace('"', '&quot;').replace("'", "\\'").replace("\n", " ")
    st.markdown("")
    wa_msg=f"KayaSparsha Prescription\nPatient: {p_name}\nDiagnosis: {rx.get('diagnosis','')}\nMedication: {rx.get('oral_medication','')}\nDoctor: Dr. {dr_name}\nDate: {rx['created_at'][:10]}"

    c1,c2,c3=st.columns(3)
    c1.link_button("💬 WhatsApp",f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}", use_container_width=True)
    c2.link_button("📱 SMS",f"sms:{phone}?body={urllib.parse.quote(wa_msg[:160])}", use_container_width=True)

    # JavaScript print button that prints ONLY the prescription content
    print_js = f"""
    <button onclick="printRx()" style="width:100%;padding:10px 20px;background:#2D5016;color:white;border:none;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer;">
        🖨️ Print Prescription
    </button>
    <script>
    function printRx() {{
        var content = document.getElementById('printable-rx');
        if (!content) {{ alert('Prescription not found'); return; }}
        var win = window.open('', '_blank');
        win.document.write('<html><head><title>KayaSparsha Prescription</title>');
        win.document.write('<style>body{{font-family:Georgia,serif;max-width:700px;margin:0 auto;padding:20px;}} @media print{{body{{padding:0;}}}} img{{max-width:160px;display:block;margin:0 auto;}}</style>');
        win.document.write('</head><body>');
        win.document.write(content.innerHTML);
        win.document.write('</body></html>');
        win.document.close();
        win.onload = function() {{ win.print(); }};
    }}
    </script>
    """
    with c3:
        st.markdown(print_js, unsafe_allow_html=True)


def prescriptions_page():
    st.markdown("<div class='page-title'>Prescriptions</div>", unsafe_allow_html=True)
    prescriptions=db.get_generated_prescriptions()
    if not prescriptions: st.info("No prescriptions generated yet"); return
    for r in prescriptions:
        p=r.get("patients",{}); d=r.get("users",{})
        c1,c2,c3,c4,c5=st.columns([1,2,1.5,1.5,1])
        c1.markdown(f"**`{p.get('patient_uid','')}`**"); c2.write(f"{p.get('first_name','')} {p.get('last_name','')}"); c3.write(f"Dr. {d.get('full_name','')}"); c4.write(r["created_at"][:10])
        if c5.button("View Rx",key=f"rxv_{r['id']}",use_container_width=True):
            st.session_state.selected_consultation_id=r["id"]; st.session_state.selected_patient_id=r["patient_id"]; st.session_state.page="view_prescription"; st.rerun()
        st.divider()


# ═══════════════════════════════════════════════════════════════════
#  INVOICES (with KayaSparsha logo)
# ═══════════════════════════════════════════════════════════════════

def invoices_page():
    user=st.session_state.user; can_create=user["role"] in ("receptionist","super_admin")
    st.markdown("<div class='page-title'>Invoices</div>", unsafe_allow_html=True)
    tabs=["📋 All Invoices"]+(["➕ Create Invoice"] if can_create else []); tab_list=st.tabs(tabs)
    with tab_list[0]:
        invoices=db.get_invoices()
        if not invoices: st.info("No invoices yet")
        else:
            for inv in invoices:
                p=inv.get("patients",{}); c1,c2,c3,c4,c5=st.columns([1.2,2,1.2,1,1])
                c1.markdown(f"**`{inv['invoice_number']}`**"); c2.write(f"{p.get('first_name','')} {p.get('last_name','')}"); c3.write(f"₹{float(inv['grand_total']):,.0f}"); c4.write(f"{'🟢' if inv['payment_status']=='paid' else '🟡'} {inv['payment_status']}")
                if c5.button("View",key=f"inv_{inv['id']}",use_container_width=True): st.session_state.selected_invoice_id=inv["id"]; st.session_state.page="view_invoice"; st.rerun()
                st.divider()
    if can_create and len(tab_list)>1:
        with tab_list[1]:
            patients=db.get_patients(); services=db.get_services()
            patient_map={f"{p['patient_uid']} — {p['first_name']} {p['last_name']}":p["id"] for p in patients}
            svc_map={f"{s['name']} (₹{s['price']})":s for s in services}
            with st.form("invf"):
                sel_p=st.selectbox("Patient *",list(patient_map.keys()) if patient_map else ["No patients"])
                st.markdown("**Line Items:**"); ni=st.number_input("Number of items",1,20,1); items=[]
                for i in range(int(ni)):
                    st.markdown(f"**Item {i+1}:**"); c1,c2,c3=st.columns([2,1,1])
                    svc=c1.selectbox("Service",["Custom"]+list(svc_map.keys()),key=f"svc_{i}")
                    if svc!="Custom": desc=svc_map[svc]["name"]; dp=float(svc_map[svc]["price"])
                    else: desc=c1.text_input("Description",key=f"desc_{i}"); dp=0.0
                    qty=c2.number_input("Qty",1,100,1,key=f"qty_{i}"); price=c3.number_input("Price ₹",0.0,value=dp,key=f"pr_{i}")
                    items.append({"description":desc,"quantity":qty,"unit_price":price,"total_price":qty*price})
                c1,c2,c3=st.columns(3); discount=c1.number_input("Discount ₹",0.0); tax=c2.number_input("Tax ₹",0.0); payment=c3.selectbox("Payment",["cash","upi","card","bank_transfer"])
                total=sum(it["total_price"] for it in items); grand=total-discount+tax
                st.markdown(f"### Grand Total: ₹{grand:,.2f}")
                if st.form_submit_button("💾 Create Invoice",type="primary",use_container_width=True):
                    if patient_map:
                        result=db.create_invoice({"patient_id":patient_map[sel_p],"total_amount":total,"discount":discount,"tax":tax,"grand_total":grand,"payment_method":payment,"payment_status":"paid","created_by":user["id"]},items)
                        if result: st.success(f"✅ Invoice **{result['invoice_number']}** created!"); st.balloons()

def view_invoice_page():
    inv_id=st.session_state.get("selected_invoice_id")
    if not inv_id: st.session_state.page="invoices"; st.rerun(); return
    inv=db.get_invoice(inv_id)
    if not inv: st.error("Not found"); return
    if st.button("← Back to Invoices"): st.session_state.page="invoices"; st.rerun()
    p=inv.get("patients",{}); logo_html=logo_img_tag(140)
    p_name = f"{p.get('first_name','')} {p.get('last_name','')}"
    phone = p.get("phone","")

    items_html="".join(f"<tr><td style='padding:8px'>{it['description']}</td><td style='padding:8px;text-align:center'>{it['quantity']}</td><td style='padding:8px;text-align:right'>₹{float(it['unit_price']):,.0f}</td><td style='padding:8px;text-align:right;font-weight:600'>₹{float(it['total_price']):,.0f}</td></tr>" for it in inv.get("items",[]))

    discount_html = f"<br/>Discount: -₹{float(inv['discount']):,.0f}" if float(inv.get('discount',0))>0 else ""
    tax_html = f"<br/>Tax: +₹{float(inv['tax']):,.0f}" if float(inv.get('tax',0))>0 else ""

    st.markdown(f"""
    <div id="printable-inv" style="border:2px solid #2D5016;border-radius:12px;padding:24px;background:white;max-width:650px;">
        <div style="text-align:center;border-bottom:3px double #2D5016;padding-bottom:12px;margin-bottom:16px;">
            {logo_html}
            <p style="color:#6B705C;font-size:12px;margin-top:4px;">TAX INVOICE</p>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:16px;">
            <div><strong>Bill To:</strong><br/>{p_name}<br/>{phone}<br/>{p.get('address','')} {p.get('city','')}</div>
            <div style="text-align:right"><strong>Invoice #:</strong> {inv['invoice_number']}<br/><strong>Date:</strong> {inv['created_at'][:10]}<br/><strong>Status:</strong> {inv['payment_status']}</div>
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <thead><tr style="border-bottom:2px solid #2D5016">
                <th style="text-align:left;padding:8px">Description</th>
                <th style="text-align:center;padding:8px">Qty</th>
                <th style="text-align:right;padding:8px">Price</th>
                <th style="text-align:right;padding:8px">Total</th>
            </tr></thead>
            <tbody>{items_html}</tbody>
        </table>
        <div style="text-align:right;margin-top:16px;font-size:13px;">
            Subtotal: ₹{float(inv['total_amount']):,.0f}{discount_html}{tax_html}
        </div>
        <div style="text-align:right;font-size:22px;font-weight:800;color:#2D5016;margin-top:8px;">₹{float(inv['grand_total']):,.0f}</div>
        <p style="text-align:center;margin-top:30px;color:#6B705C;font-size:12px;">Thank you for choosing KayaSparsha Ayurvedic Clinic</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("")
    wa_msg=f"KayaSparsha Invoice {inv['invoice_number']}\nPatient: {p_name}\nTotal: ₹{float(inv['grand_total']):,.0f}\nDate: {inv['created_at'][:10]}\nThank you!"
    c1,c2,c3=st.columns(3)
    c1.link_button("💬 WhatsApp",f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}",use_container_width=True)
    c2.link_button("📱 SMS",f"sms:{phone}?body={urllib.parse.quote(wa_msg[:160])}",use_container_width=True)

    # JavaScript print button that prints ONLY the invoice content
    print_js = """
    <button onclick="printInv()" style="width:100%;padding:10px 20px;background:#2D5016;color:white;border:none;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer;">
        🖨️ Print Invoice
    </button>
    <script>
    function printInv() {
        var content = document.getElementById('printable-inv');
        if (!content) { alert('Invoice not found'); return; }
        var win = window.open('', '_blank');
        win.document.write('<html><head><title>KayaSparsha Invoice</title>');
        win.document.write('<style>body{font-family:Georgia,serif;max-width:650px;margin:0 auto;padding:20px;} @media print{body{padding:0;}} img{max-width:140px;display:block;margin:0 auto;} table{width:100%;border-collapse:collapse;} th,td{padding:8px;}</style>');
        win.document.write('</head><body>');
        win.document.write(content.innerHTML);
        win.document.write('</body></html>');
        win.document.close();
        win.onload = function() { win.print(); };
    }
    </script>
    """
    with c3:
        st.markdown(print_js, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SERVICES, USERS, REPORTS
# ═══════════════════════════════════════════════════════════════════

def services_page():
    st.markdown("<div class='page-title'>Services & Pricing</div>", unsafe_allow_html=True)
    tab1,tab2=st.tabs(["📋 All Services","➕ Add Service"])
    with tab1:
        services=db.get_services()
        if not services: st.info("No services yet.")
        else:
            st.dataframe(pd.DataFrame(services)[["name","category","price","description"]].rename(columns={"name":"Name","category":"Category","price":"Price (₹)","description":"Description"}),use_container_width=True,hide_index=True)
            svc_names={s["name"]:s for s in services}; sel=st.selectbox("Select service to edit",list(svc_names.keys())); svc=svc_names[sel]
            with st.form("es"):
                cats=["consultation","panchakarma","therapy","other","general"]
                nn=st.text_input("Name",value=svc["name"]); c1,c2=st.columns(2)
                nc=c1.selectbox("Category",cats,index=cats.index(svc["category"]) if svc["category"] in cats else 4); np=c2.number_input("Price ₹",value=float(svc["price"])); nd=st.text_input("Description",value=svc.get("description") or "")
                b1,b2=st.columns(2)
                if b1.form_submit_button("💾 Update",use_container_width=True): db.update_service(svc["id"],{"name":nn,"category":nc,"price":np,"description":nd}); st.success("Updated!"); st.rerun()
                if b2.form_submit_button("🗑️ Delete",use_container_width=True): db.delete_service(svc["id"]); st.success("Deleted!"); st.rerun()
    with tab2:
        with st.form("as"):
            name=st.text_input("Service Name *"); c1,c2=st.columns(2); cat=c1.selectbox("Category",["consultation","panchakarma","therapy","other","general"]); price=c2.number_input("Price ₹ *",0.0); desc=st.text_input("Description")
            if st.form_submit_button("➕ Add Service",type="primary",use_container_width=True):
                if name: db.create_service({"name":name,"category":cat,"price":price,"description":desc}); st.success(f"✅ '{name}' added!"); st.rerun()

def users_page():
    st.markdown("<div class='page-title'>User Management</div>", unsafe_allow_html=True)
    tab1,tab2=st.tabs(["👥 All Users","➕ Add User"])
    with tab1:
        users=db.get_users()
        if users:
            df=pd.DataFrame(users)[["username","full_name","role","qualification","registration_no","is_active"]]; df["Status"]=df["is_active"].apply(lambda x:"Active" if x else "Inactive")
            st.dataframe(df[["username","full_name","role","qualification","registration_no","Status"]].rename(columns={"username":"Username","full_name":"Name","role":"Role","qualification":"Qualification","registration_no":"Reg No."}),use_container_width=True,hide_index=True)
    with tab2:
        with st.form("au"):
            c1,c2=st.columns(2); fn=c1.text_input("Full Name *"); un=c2.text_input("Username *"); pw=c1.text_input("Password *",type="password"); role=c2.selectbox("Role *",["receptionist","doctor","super_admin"]); qual=c1.text_input("Qualification",placeholder="e.g., BAMS, MD Ayurveda"); rno=c2.text_input("Registration No.")
            if st.form_submit_button("➕ Create User",type="primary",use_container_width=True):
                if not fn or not un or not pw: st.error("Fill all required fields")
                else:
                    try: db.create_user({"username":un,"password":pw,"full_name":fn,"role":role,"qualification":qual,"registration_no":rno}); st.success(f"✅ User '{un}' created!"); st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

def reports_page():
    st.markdown("<div class='page-title'>Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Export clinic data and view income analytics</div>", unsafe_allow_html=True)

    # ─── Income Analytics Section ──────────────────────────────────
    st.subheader("💰 Income Analytics")

    invoices_data = db.get_income_analytics()
    now = datetime.date.today()

    if invoices_data:
        # Build a dataframe with date parsing
        inv_df = pd.DataFrame(invoices_data)
        inv_df["amount"] = inv_df["grand_total"].astype(float)
        inv_df["date"] = pd.to_datetime(inv_df["created_at"]).dt.date
        inv_df["week"] = pd.to_datetime(inv_df["created_at"]).dt.isocalendar().week
        inv_df["month"] = pd.to_datetime(inv_df["created_at"]).dt.month
        inv_df["month_name"] = pd.to_datetime(inv_df["created_at"]).dt.strftime("%B %Y")
        inv_df["year"] = pd.to_datetime(inv_df["created_at"]).dt.year

        # Period selector
        period = st.radio("View income by:", ["This Week", "This Month", "This Year", "All Time", "Custom Range"], horizontal=True)

        if period == "This Week":
            week_start = now - datetime.timedelta(days=now.weekday())
            filtered = inv_df[inv_df["date"] >= week_start]
            title = f"Week of {week_start.strftime('%d %b %Y')}"
        elif period == "This Month":
            filtered = inv_df[(inv_df["month"] == now.month) & (inv_df["year"] == now.year)]
            title = now.strftime("%B %Y")
        elif period == "This Year":
            filtered = inv_df[inv_df["year"] == now.year]
            title = str(now.year)
        elif period == "Custom Range":
            c1, c2 = st.columns(2)
            start_date = c1.date_input("From", value=now - datetime.timedelta(days=30))
            end_date = c2.date_input("To", value=now)
            filtered = inv_df[(inv_df["date"] >= start_date) & (inv_df["date"] <= end_date)]
            title = f"{start_date.strftime('%d %b')} — {end_date.strftime('%d %b %Y')}"
        else:
            filtered = inv_df
            title = "All Time"

        # Summary cards
        total_income = filtered["amount"].sum()
        total_transactions = len(filtered)
        avg_per_day = total_income / max((filtered["date"].nunique()), 1)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-card'><p class='stat-label'>Total Income ({title})</p><p class='stat-value'>₹{total_income:,.0f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-card'><p class='stat-label'>Transactions</p><p class='stat-value'>{total_transactions}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><p class='stat-label'>Avg / Day</p><p class='stat-value'>₹{avg_per_day:,.0f}</p></div>", unsafe_allow_html=True)

        # Monthly breakdown table
        st.markdown("")
        st.subheader("📊 Monthly Breakdown")
        monthly = inv_df.groupby("month_name").agg(
            Income=("amount", "sum"),
            Transactions=("amount", "count"),
        ).reset_index()
        monthly.columns = ["Month", "Income (₹)", "Transactions"]
        monthly["Income (₹)"] = monthly["Income (₹)"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(monthly, use_container_width=True, hide_index=True)

        # Payment method breakdown
        st.subheader("💳 By Payment Method")
        by_method = filtered.groupby("payment_method").agg(
            Income=("amount", "sum"),
            Count=("amount", "count"),
        ).reset_index()
        by_method.columns = ["Payment Method", "Income (₹)", "Transactions"]
        by_method["Income (₹)"] = by_method["Income (₹)"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(by_method, use_container_width=True, hide_index=True)

        # Download consolidated income report
        st.markdown("")
        st.subheader("📥 Download Consolidated Income Report")
        income_report = inv_df[["date", "amount", "payment_method"]].copy()
        income_report.columns = ["Date", "Amount (₹)", "Payment Method"]
        income_report = income_report.sort_values("Date", ascending=False)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            income_report.to_excel(writer, sheet_name="All Transactions", index=False)
            # Monthly summary sheet
            monthly_raw = inv_df.groupby("month_name").agg(Income=("amount","sum"), Transactions=("amount","count")).reset_index()
            monthly_raw.columns = ["Month", "Total Income (₹)", "Transactions"]
            monthly_raw.to_excel(writer, sheet_name="Monthly Summary", index=False)
        st.download_button("📥 Download Income Report (Excel)", output.getvalue(), "income_report.xlsx", use_container_width=True)

    else:
        st.info("No paid invoices yet. Income data will appear once invoices are generated.")

    # ─── Data Export Section ───────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Data Exports")

    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("<div class='stat-card' style='text-align:center'><p style='font-size:40px;margin:0'>👥</p><p style='font-weight:700;font-size:16px'>Patient Report</p></div>",unsafe_allow_html=True)
        data=db.get_patients_report()
        if data: o=io.BytesIO(); pd.DataFrame(data).to_excel(o,index=False,engine="xlsxwriter"); st.download_button("📥 Download",o.getvalue(),"patients_report.xlsx",use_container_width=True, key="dl_patients")
    with c2:
        st.markdown("<div class='stat-card' style='text-align:center'><p style='font-size:40px;margin:0'>🧾</p><p style='font-weight:700;font-size:16px'>Invoice Report</p></div>",unsafe_allow_html=True)
        data=db.get_invoices_report()
        if data:
            rows=[]
            for d in data: p=d.pop("patients",{}); d["patient_uid"]=p.get("patient_uid",""); d["patient_name"]=f"{p.get('first_name','')} {p.get('last_name','')}"; rows.append(d)
            o=io.BytesIO(); pd.DataFrame(rows).to_excel(o,index=False,engine="xlsxwriter"); st.download_button("📥 Download",o.getvalue(),"invoices_report.xlsx",use_container_width=True, key="dl_invoices")
    with c3:
        st.markdown("<div class='stat-card' style='text-align:center'><p style='font-size:40px;margin:0'>🩺</p><p style='font-weight:700;font-size:16px'>Consultation Report</p></div>",unsafe_allow_html=True)
        data=db.get_consultations_report()
        if data:
            rows=[]
            for d in data: p=d.pop("patients",{}); u=d.pop("users",{}); d["patient_uid"]=p.get("patient_uid",""); d["patient_name"]=f"{p.get('first_name','')} {p.get('last_name','')}"; d["doctor"]=u.get("full_name",""); rows.append(d)
            o=io.BytesIO(); pd.DataFrame(rows).to_excel(o,index=False,engine="xlsxwriter"); st.download_button("📥 Download",o.getvalue(),"consultations_report.xlsx",use_container_width=True, key="dl_consults")


# ═══════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════

def main():
    if not st.session_state.logged_in: login_page(); return
    render_sidebar()
    pages={"dashboard":dashboard_page,"patients":patients_page,"register_patient":register_patient_page,"patient_detail":patient_detail_page,"new_consultation":new_consultation_page,"add_follow_up":add_follow_up_page,"consultations":consultations_page,"prescriptions":prescriptions_page,"view_prescription":view_prescription_page,"invoices":invoices_page,"view_invoice":view_invoice_page,"services":services_page,"users":users_page,"reports":reports_page}
    pages.get(st.session_state.page, dashboard_page)()

if __name__ == "__main__":
    main()
