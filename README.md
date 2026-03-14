# 🌿 KayaSparsha - Ayurvedic Clinic Management System

Internal tool for KayaSparsha Ayurvedic Clinic. Built with **Streamlit + Supabase PostgreSQL**.

---

## Setup Guide (One-Time)

### Step 1: Create Supabase Project (Free)

1. Go to [supabase.com](https://supabase.com) → Sign up with GitHub
2. Click **"New Project"**
3. Give it a name (e.g., `kayasparsha`), set a database password, choose a region close to you (e.g., Mumbai)
4. Wait ~2 minutes for the project to be created

### Step 2: Get Your Keys

1. In your Supabase project, go to **Settings → API**
2. Copy these two values:
   - **Project URL** → looks like `https://abcdefg.supabase.co`
   - **service_role key** (under "Project API keys") → the long key labeled `service_role` (NOT the `anon` key)

> ⚠️ Use the **service_role** key, not the anon key. This gives the app full database access.

### Step 3: Create Database Tables

1. In Supabase, go to **SQL Editor** (left sidebar)
2. Click **"New Query"**
3. Copy-paste the entire contents of **`schema.sql`** from this repo
4. Click **"Run"**
5. You should see "Success. No rows returned" — that means all tables are created

### Step 4: Deploy to Streamlit Cloud

1. Push this repo to GitHub:
   ```bash
   git init
   git add .
   git commit -m "KayaSparsha clinic app"
   git remote add origin https://github.com/YOUR_USERNAME/kayasparsha.git
   git branch -M main
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) → Sign in with GitHub

3. Click **"New app"** → Select your repo → Main file: `app.py`

4. Before deploying, click **"Advanced settings"** → **"Secrets"** and paste:
   ```toml
   SUPABASE_URL = "https://YOUR-PROJECT-ID.supabase.co"
   SUPABASE_KEY = "YOUR-SERVICE-ROLE-KEY"
   ```

5. Click **Deploy** — your app will be live in ~2 minutes!

### Step 5: First Login

1. Open your app URL (e.g., `https://kayasparsha.streamlit.app`)
2. Login: **admin** / **admin123**
3. Go to **Users** → Create doctor and receptionist accounts
4. Go to **Services** → Add your services:
   - Consultation Fee (e.g., ₹500)
   - Panchakarma treatments (Vamana, Virechana, Basti, Nasya, Raktamokshana)
   - Snehapana, Shirodhara, Abhyanga, etc.

---

## Running Locally (Optional)

```bash
pip install -r requirements.txt

# Create secrets file
cp secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Supabase credentials

streamlit run app.py
```

---

## Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application (UI + routing) |
| `db.py` | All database operations via Supabase |
| `schema.sql` | Database schema — run in Supabase SQL Editor |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Streamlit theme (Ayurvedic green) |
| `secrets.toml.example` | Template for Supabase credentials |

---

## Features

- **Patient Registration** with auto-generated UID (KS-YYYYMM-0001)
- **Doctor Consultation** form (complaint, history, examination, diagnosis, treatment)
- **Prescription Generation** with doctor name, print, WhatsApp & SMS sharing
- **Follow-up Management** for returning patients
- **Invoice System** with service catalog, discounts, tax, multiple payment methods
- **Role-Based Access** (Receptionist, Doctor, Super Admin)
- **Reports Export** to Excel
- **Supabase PostgreSQL** — persistent cloud database

## Role Permissions

| Feature | Receptionist | Doctor | Super Admin |
|---------|-------------|--------|-------------|
| Register Patients | ✅ | ❌ | ✅ |
| View Patient Info | ✅ | ✅ | ✅ |
| View Medical History | ❌ | ✅ | ✅ |
| Create Consultation | ❌ | ✅ | ✅ |
| Generate Prescription | ❌ | ✅ | ✅ |
| View Prescriptions | ✅ | ✅ | ✅ |
| Create Invoice | ✅ | ❌ | ✅ |
| Manage Services/Users | ❌ | ❌ | ✅ |
| Export Reports | ❌ | ❌ | ✅ |
