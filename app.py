"""
Qur'an Khuwani Service — Streamlit fullstack app
Services:
  1. Qur'an Khuwani Appointment (hourly charge in PKR, address, date, time)
  2. Grave Renovation Service (Normal / Good / Renew, graveyard address, date, time)
Users must sign up / log in to make a booking.
Run locally with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, time

import db

st.set_page_config(page_title="Qur'an Khuwani Service", page_icon="🕌", layout="wide")

db.init_db()

if "user" not in st.session_state:
    st.session_state.user = None


def render_booking_manager(table_name, rows):
    """Admin controls to confirm, cancel, or delete a single booking."""
    if not rows:
        return
    ids = [r["id"] for r in rows]
    id_to_row = {r["id"]: r for r in rows}

    st.markdown("**Manage a booking**")
    selected_id = st.selectbox("Booking ID", ids, key=f"select_{table_name}")
    current_status = id_to_row[selected_id]["status"]
    st.write(f"Current status: **{current_status}**")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✅ Confirm", key=f"confirm_{table_name}"):
            db.update_status(table_name, selected_id, "Confirmed")
            st.success(f"Booking #{selected_id} marked Confirmed.")
            st.rerun()
    with c2:
        if st.button("❌ Cancel Appointment", key=f"cancel_{table_name}"):
            db.update_status(table_name, selected_id, "Cancelled")
            st.success(f"Booking #{selected_id} marked Cancelled.")
            st.rerun()
    with c3:
        if st.button("🗑️ Delete", key=f"delete_{table_name}"):
            db.delete_booking(table_name, selected_id)
            st.success(f"Booking #{selected_id} deleted.")
            st.rerun()

# ---------------------------------------------------------------- styling --
st.markdown(
    """
    <style>
    .main-header { text-align:center; padding: 1rem 0 0.5rem 0; }
    .service-card {
        background:#f7f7f9; border-radius:12px; padding:1.2rem;
        border:1px solid #e6e6e6; margin-bottom:1rem; height:100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("🕌 Qur'an Khuwani Service")

if st.session_state.user:
    st.sidebar.success(f"Logged in as **{st.session_state.user['username']}**")
    if st.sidebar.button("Log out"):
        st.session_state.user = None
        st.rerun()
    nav_options = [
        "Home",
        "Qur'an Khuwani Appointment",
        "Grave Renovation Service",
        "My Bookings",
        "Admin Dashboard",
    ]
else:
    nav_options = ["Home", "Login / Sign Up", "Admin Dashboard"]

page = st.sidebar.radio("Navigate", nav_options)

# ============================================================== HOME =====
if page == "Home":
    st.markdown(
        "<div class='main-header'><h1>Qur'an Khuwani Service</h1>"
        "<p>Book a Qur'an Khuwani appointment or a Grave Renovation service, "
        "with transparent charges in PKR.</p></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='service-card'>", unsafe_allow_html=True)
        st.subheader("📖 Qur'an Khuwani Appointment")
        st.write(
            "Book a Qari/Qaria for Qur'an Khuwani at your preferred address, "
            "date and time. Charged hourly in PKR."
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='service-card'>", unsafe_allow_html=True)
        st.subheader("🪦 Grave Renovation Service")
        st.write(
            "Choose from Normal, Good, or Renew renovation quality for a "
            "grave at the graveyard of your choice."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.user:
        st.info("Use the sidebar to book a service, view your bookings, or check the admin dashboard.")
    else:
        st.warning("Please **Log In / Sign Up** from the sidebar to book a service.")

# ===================================================== LOGIN / SIGN UP ===
elif page == "Login / Sign Up":
    st.header("👤 Account")
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            if submitted:
                user = db.authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose a username")
            new_email = st.text_input("Email (optional)")
            new_password = st.text_input("Choose a password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                if not new_username or not new_password:
                    st.error("Username and password are required.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password should be at least 6 characters.")
                else:
                    ok, result = db.create_user(new_username, new_email, new_password)
                    if ok:
                        st.session_state.user = result
                        st.success("Account created! You're now logged in.")
                        st.rerun()
                    else:
                        st.error(result)

# ============================================== QUR'AN KHUWANI BOOKING ===
elif page == "Qur'an Khuwani Appointment":
    if not st.session_state.user:
        st.warning("Please log in to book this service.")
    else:
        st.header("📖 Book Qur'an Khuwani Appointment")
        default_rate = float(db.get_setting("quran_default_rate", 500))

        with st.form("quran_form", clear_on_submit=True):
            name = st.text_input("Full Name *")
            contact = st.text_input("Contact Number *")
            address = st.text_area("Address (where Khuwani will be held) *")

            c1, c2, c3 = st.columns(3)
            with c1:
                booking_date = st.date_input("Date *", min_value=date.today())
            with c2:
                booking_time = st.time_input("Time *", value=time(9, 0))
            with c3:
                hours = st.number_input("Duration (hours) *", min_value=1.0, step=0.5, value=1.0)

            rate_per_hour = st.number_input(
                "Rate per hour (PKR) *", min_value=0.0, value=default_rate, step=50.0
            )
            notes = st.text_area("Additional notes (optional)")

            estimated_total = round(hours * rate_per_hour, 2)
            st.markdown(f"### Estimated Charges: **PKR {estimated_total:,.0f}**")

            submitted = st.form_submit_button("Confirm Booking")
            if submitted:
                if not name or not contact or not address:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    total = db.add_quran_booking(
                        name, contact, address, booking_date, booking_time,
                        hours, rate_per_hour, notes, user_id=st.session_state.user["id"],
                    )
                    st.success(
                        f"Booking confirmed for {name} on {booking_date} at {booking_time}. "
                        f"Total charge: PKR {total:,.0f}"
                    )

# ============================================== GRAVE RENOVATION BOOKING =
elif page == "Grave Renovation Service":
    if not st.session_state.user:
        st.warning("Please log in to book this service.")
    else:
        st.header("🪦 Book Grave Renovation Service")

        prices = {
            "Normal": float(db.get_setting("grave_normal_price", 3000)),
            "Good": float(db.get_setting("grave_good_price", 6000)),
            "Renew": float(db.get_setting("grave_renew_price", 10000)),
        }

        st.write("**Quality & Pricing (PKR):**")
        p1, p2, p3 = st.columns(3)
        p1.metric("Normal", f"PKR {prices['Normal']:,.0f}")
        p2.metric("Good", f"PKR {prices['Good']:,.0f}")
        p3.metric("Renew", f"PKR {prices['Renew']:,.0f}")

        with st.form("grave_form", clear_on_submit=True):
            name = st.text_input("Full Name *")
            contact = st.text_input("Contact Number *")
            graveyard_address = st.text_area("Graveyard Address *")

            c1, c2 = st.columns(2)
            with c1:
                service_date = st.date_input("Date *", min_value=date.today(), key="grave_date")
            with c2:
                service_time = st.time_input("Time *", value=time(9, 0), key="grave_time")

            quality = st.selectbox("Renovation Quality *", ["Normal", "Good", "Renew"])
            notes = st.text_area("Additional notes (optional)", key="grave_notes")

            charge = prices[quality]
            st.markdown(f"### Charges: **PKR {charge:,.0f}**")

            submitted = st.form_submit_button("Confirm Booking")
            if submitted:
                if not name or not contact or not graveyard_address:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    db.add_grave_booking(
                        name, contact, graveyard_address, service_date, service_time,
                        quality, charge, notes, user_id=st.session_state.user["id"],
                    )
                    st.success(
                        f"Booking confirmed for {name} on {service_date} at {service_time}. "
                        f"Quality: {quality}. Charge: PKR {charge:,.0f}"
                    )

# ==================================================== MY BOOKINGS PAGE ===
elif page == "My Bookings":
    st.header("🧾 My Bookings")
    if not st.session_state.user:
        st.warning("Please log in to view your bookings.")
    else:
        uid = st.session_state.user["id"]
        st.subheader("Qur'an Khuwani Appointments")
        rows = db.get_user_quran_bookings(uid)
        if rows:
            df = pd.DataFrame([dict(r) for r in rows])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("You have no Qur'an Khuwani bookings yet.")

        st.subheader("Grave Renovation Bookings")
        rows = db.get_user_grave_bookings(uid)
        if rows:
            df = pd.DataFrame([dict(r) for r in rows])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("You have no Grave Renovation bookings yet.")

# ========================================================= ADMIN PANEL ==
elif page == "Admin Dashboard":
    st.header("🔐 Admin Dashboard")

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pwd = st.text_input("Enter admin password", type="password")
        try:
            admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
        except Exception:
            admin_password = "admin123"

        if st.button("Login"):
            if pwd == admin_password:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.caption(
            "Default password is `admin123` for local testing. "
            "Set your own via Streamlit secrets (`ADMIN_PASSWORD`) before deploying."
        )
    else:
        tab1, tab2, tab3 = st.tabs(
            ["Qur'an Khuwani Bookings", "Grave Renovation Bookings", "Settings"]
        )

        with tab1:
            rows = db.get_all_quran_bookings()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                st.dataframe(df, use_container_width=True)
                c1, c2 = st.columns(2)
                c1.metric("Total Bookings", len(df))
                c2.metric("Total Revenue (PKR)", f"{df['total_charge'].sum():,.0f}")
                st.divider()
                render_booking_manager("quran_bookings", rows)
            else:
                st.info("No bookings yet.")

        with tab2:
            rows = db.get_all_grave_bookings()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                st.dataframe(df, use_container_width=True)
                c1, c2 = st.columns(2)
                c1.metric("Total Bookings", len(df))
                c2.metric("Total Revenue (PKR)", f"{df['charge'].sum():,.0f}")
                st.divider()
                render_booking_manager("grave_bookings", rows)
            else:
                st.info("No bookings yet.")

        with tab3:
            st.subheader("Default Pricing")
            new_rate = st.number_input(
                "Default Qur'an Khuwani rate/hour (PKR)",
                value=float(db.get_setting("quran_default_rate", 500)),
            )
            new_normal = st.number_input(
                "Grave Renovation - Normal (PKR)",
                value=float(db.get_setting("grave_normal_price", 3000)),
            )
            new_good = st.number_input(
                "Grave Renovation - Good (PKR)",
                value=float(db.get_setting("grave_good_price", 6000)),
            )
            new_renew = st.number_input(
                "Grave Renovation - Renew (PKR)",
                value=float(db.get_setting("grave_renew_price", 10000)),
            )
            if st.button("Save Settings"):
                db.set_setting("quran_default_rate", new_rate)
                db.set_setting("grave_normal_price", new_normal)
                db.set_setting("grave_good_price", new_good)
                db.set_setting("grave_renew_price", new_renew)
                st.success("Settings updated.")

        if st.button("Log out"):
            st.session_state.admin_ok = False
            st.rerun()
