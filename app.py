"""
Qur'an Khuwani Service — Streamlit fullstack app
Services:
  1. Qur'an Khuwani Appointment (hourly charge in PKR, address, date, time)
  2. Grave Renovation Service (Normal / Good / Renew, graveyard address, date, time)
Run locally with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, time

import db

st.set_page_config(page_title="Qur'an Khuwani Service", page_icon="🕌", layout="wide")

db.init_db()

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
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Qur'an Khuwani Appointment", "Grave Renovation Service", "Admin Dashboard"],
)

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

    st.info("Use the sidebar to book a service or view the admin dashboard.")

# ============================================== QUR'AN KHUWANI BOOKING ===
elif page == "Qur'an Khuwani Appointment":
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
                    hours, rate_per_hour, notes,
                )
                st.success(
                    f"Booking confirmed for {name} on {booking_date} at {booking_time}. "
                    f"Total charge: PKR {total:,.0f}"
                )

# ============================================== GRAVE RENOVATION BOOKING =
elif page == "Grave Renovation Service":
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
                    quality, charge, notes,
                )
                st.success(
                    f"Booking confirmed for {name} on {service_date} at {service_time}. "
                    f"Quality: {quality}. Charge: PKR {charge:,.0f}"
                )

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
