-- ═══════════════════════════════════════════════════════════════════
--  KayaSparsha - Supabase Database Schema
--  Run this in Supabase SQL Editor (https://supabase.com/dashboard)
-- ═══════════════════════════════════════════════════════════════════

-- Users table (staff accounts)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('receptionist','doctor','super_admin')),
    qualification TEXT DEFAULT '',
    registration_no TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id BIGSERIAL PRIMARY KEY,
    patient_uid TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT DEFAULT '',
    age INTEGER DEFAULT 0,
    sex TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    city TEXT DEFAULT '',
    state TEXT DEFAULT '',
    pincode TEXT DEFAULT '',
    blood_group TEXT DEFAULT '',
    emergency_contact TEXT DEFAULT '',
    emergency_phone TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    registered_by BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Consultations table
CREATE TABLE IF NOT EXISTS consultations (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(id),
    doctor_id BIGINT NOT NULL REFERENCES users(id),
    visit_type TEXT DEFAULT 'initial',
    main_complaint TEXT DEFAULT '',
    previous_medical_history TEXT DEFAULT '',
    family_history TEXT DEFAULT '',
    current_medication TEXT DEFAULT '',
    examination TEXT DEFAULT '',
    diagnosis TEXT DEFAULT '',
    oral_medication TEXT DEFAULT '',
    panchakarma_therapy TEXT DEFAULT '',
    additional_notes TEXT DEFAULT '',
    prescription_generated BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Follow-ups table
CREATE TABLE IF NOT EXISTS follow_ups (
    id BIGSERIAL PRIMARY KEY,
    consultation_id BIGINT NOT NULL REFERENCES consultations(id),
    doctor_id BIGINT NOT NULL REFERENCES users(id),
    follow_up_complaint TEXT DEFAULT '',
    follow_up_examination TEXT DEFAULT '',
    follow_up_diagnosis TEXT DEFAULT '',
    follow_up_oral_medication TEXT DEFAULT '',
    follow_up_panchakarma TEXT DEFAULT '',
    follow_up_notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Services table (clinic services catalog)
CREATE TABLE IF NOT EXISTS services (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    price NUMERIC NOT NULL DEFAULT 0,
    description TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_number TEXT UNIQUE NOT NULL,
    patient_id BIGINT NOT NULL REFERENCES patients(id),
    consultation_id BIGINT,
    total_amount NUMERIC NOT NULL DEFAULT 0,
    discount NUMERIC DEFAULT 0,
    tax NUMERIC DEFAULT 0,
    grand_total NUMERIC NOT NULL DEFAULT 0,
    payment_method TEXT DEFAULT 'cash',
    payment_status TEXT DEFAULT 'pending',
    notes TEXT DEFAULT '',
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoice line items
CREATE TABLE IF NOT EXISTS invoice_items (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL REFERENCES invoices(id),
    service_id BIGINT,
    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price NUMERIC NOT NULL,
    total_price NUMERIC NOT NULL
);

-- ═══════════════════════════════════════════════════════════════════
--  Insert default super admin (password: admin123)
--  SHA-256 hash of "admin123"
-- ═══════════════════════════════════════════════════════════════════
INSERT INTO users (username, password_hash, full_name, role)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Super Admin', 'super_admin')
ON CONFLICT (username) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════
--  Enable Row Level Security (RLS) - IMPORTANT for Supabase
--  We disable RLS since this is an internal tool with app-level auth
-- ═══════════════════════════════════════════════════════════════════
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE consultations ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;

-- Allow the service_role key full access (used by our app)
CREATE POLICY "Service role full access" ON users FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON patients FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON consultations FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON follow_ups FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON services FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON invoices FOR ALL USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY "Service role full access" ON invoice_items FOR ALL USING (TRUE) WITH CHECK (TRUE);
