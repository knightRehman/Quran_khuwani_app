# Qur'an Khuwani Service

A fullstack web app (Python + Streamlit + SQLite) for booking:

1. **Qur'an Khuwani Appointment** — hourly rate (PKR), address, date, time.
2. **Grave Renovation Service** — quality tiers (Normal / Good / Renew), graveyard address, date, time.

Streamlit acts as both frontend (forms/UI) and backend (Python logic), with SQLite (`db.py`) as the data layer — no separate server needed.

## Project structure

```
quran_khuwani_service/
├── app.py            # Streamlit frontend + app logic (entry point)
├── db.py             # SQLite backend (bookings + settings)
├── requirements.txt  # Python dependencies
└── README.md
```

## 1. Run it locally

```bash
cd quran_khuwani_service
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

Default admin password (Admin Dashboard tab): `admin123` — change this before deploying (see step 3 below).

## 2. Push to GitHub

Streamlit Community Cloud deploys directly from a GitHub repo.

```bash
cd quran_khuwani_service
git init
git add .
git commit -m "Initial commit: Qur'an Khuwani Service app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

(Create the empty repo on GitHub first if you haven't already.)

## 3. Deploy on Streamlit Community Cloud

1. Go to **https://share.streamlit.io** and sign in with your GitHub account.
2. Click **"Create app"** → **"Deploy a public app from GitHub"**.
3. Select your repository, the `main` branch, and set the main file path to `app.py`.
4. Before deploying (or after, via **App settings → Secrets**), add your own admin password so it's not the default:
   ```toml
   ADMIN_PASSWORD = "your-strong-password"
   ```
5. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically and gives you a public URL like:
   `https://<your-app-name>.streamlit.app`

## Notes on the SQLite database on Streamlit Cloud

Streamlit Community Cloud's filesystem is **ephemeral** — the `quran_khuwani.db` file can be reset when the app restarts or redeploys (e.g., after inactivity or a new push). This is fine for a demo or low-traffic use, but for production you should swap the storage layer for a persistent database such as:

- **Supabase** or **Neon** (free-tier Postgres), or
- **Turso** (hosted SQLite/libSQL), or
- **Google Sheets** via a service account (simplest, no new infra).

Only `db.py` would need to change — `app.py` calls it through simple functions (`add_quran_booking`, `add_grave_booking`, `get_all_quran_bookings`, etc.), so swapping the backend later is a contained change. Ask if you'd like me to wire one of these up.

## Customizing pricing

Default prices (editable anytime from **Admin Dashboard → Settings** once the app is running):

| Service | Tier | Default Price (PKR) |
|---|---|---|
| Qur'an Khuwani | per hour | 500 |
| Grave Renovation | Normal | 3,000 |
| Grave Renovation | Good | 6,000 |
| Grave Renovation | Renew | 10,000 |
