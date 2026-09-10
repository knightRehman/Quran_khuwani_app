# Qur'an Khuwani Service

**Live app:** https://qurankhuwaniapp-ftb.streamlit.app/
**GitHub repository:** https://github.com/knightRehman/Quran_khuwani_app

A fullstack web app (Python + Streamlit + SQLite) for booking:

1. **Qur'an Khuwani Appointment** — hourly rate (PKR), address, date, time.
2. **Grave Renovation Service** — quality tiers (Normal / Good / Renew), graveyard address, date, time.

Users create their own account (sign up / log in) before booking. Streamlit acts as both frontend (forms/UI) and backend (Python logic), with SQLite (`db.py`) as the data layer — no separate server needed.

## Project structure

```
quran_khuwani_service/
├── app.py            # Streamlit frontend + app logic (entry point)
├── db.py             # SQLite backend (users, bookings, settings)
├── requirements.txt  # Python dependencies
└── README.md
```

## Features

- **User accounts** — sign up with a username, optional email, and password. Passwords are never stored in plain text; they're hashed with PBKDF2-SHA256 and a unique per-user salt.
- **Qur'an Khuwani booking** (requires login) — name, contact, address, date, time, duration (hours), rate/hour (PKR, editable) → auto-calculates total.
- **Grave Renovation booking** (requires login) — name, contact, graveyard address, date, time, quality (Normal / Good / Renew) → shows the charge for the selected tier.
- **My Bookings** — logged-in users can see their own booking history for both services, including its current status (e.g. if the admin cancels it).
- **Admin Dashboard** — separate password-protected area (not tied to a user account) showing all bookings across all users, revenue totals, editable default pricing, and per-booking controls to **Confirm**, **Cancel**, or **Delete** any Qur'an Khuwani or Grave Renovation booking.

## 1. Run it locally

```bash
cd quran_khuwani_service
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

Default admin password (Admin Dashboard tab): `admin123` — change this before deploying (see step 3 below). This is separate from regular user accounts.

## 2. Push updates to GitHub

```bash
cd quran_khuwani_service
git add .
git commit -m "Add user accounts (sign up / log in) and My Bookings page"
git push
```

Streamlit Community Cloud automatically redeploys the live app whenever you push to the connected branch.

## 3. Deploy on Streamlit Community Cloud

Already deployed at **https://qurankhuwaniapp-ftb.streamlit.app/**. If you ever need to redeploy from scratch:

1. Go to **https://share.streamlit.io** and sign in with your GitHub account.
2. Click **"Create app"** → **"Deploy a public app from GitHub"**.
3. Select your repository, the `main` branch, and set the main file path to `app.py`.
4. In **App settings → Secrets**, set:
   ```toml
   ADMIN_PASSWORD = "your-strong-password"
   ```
5. Click **Deploy**.

## Notes on the SQLite database on Streamlit Cloud

Streamlit Community Cloud's filesystem is **ephemeral** — the `quran_khuwani.db` file (including user accounts and bookings) can be reset when the app restarts or redeploys. This is fine for a demo or low-traffic use, but for real users you should swap the storage layer for a persistent database such as:

- **Supabase** or **Neon** (free-tier Postgres), or
- **Turso** (hosted SQLite/libSQL), or
- **Google Sheets** via a service account (simplest, no new infra).

Only `db.py` would need to change — `app.py` calls it through simple functions (`create_user`, `authenticate_user`, `add_quran_booking`, `add_grave_booking`, etc.), so swapping the backend later is a contained change. Ask if you'd like me to wire one of these up.

## Customizing pricing

Default prices (editable anytime from **Admin Dashboard → Settings** once the app is running):

| Service | Tier | Default Price (PKR) |
|---|---|---|
| Qur'an Khuwani | per hour | 500 |
| Grave Renovation | Normal | 3,000 |
| Grave Renovation | Good | 6,000 |
| Grave Renovation | Renew | 10,000 |
