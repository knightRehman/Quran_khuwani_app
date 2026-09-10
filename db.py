"""
db.py — SQLite backend for Qur'an Khuwani Service
Handles storage for:
  - Qur'an Khuwani appointment bookings
  - Grave Renovation Service bookings
  - Admin-editable pricing settings
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "quran_khuwani.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quran_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                address TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                hours REAL NOT NULL,
                rate_per_hour REAL NOT NULL,
                total_charge REAL NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grave_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                graveyard_address TEXT NOT NULL,
                service_date TEXT NOT NULL,
                service_time TEXT NOT NULL,
                quality TEXT NOT NULL,
                charge REAL NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        defaults = {
            "quran_default_rate": "500",
            "grave_normal_price": "3000",
            "grave_good_price": "6000",
            "grave_renew_price": "10000",
        }
        for k, v in defaults.items():
            cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        conn.commit()


def get_setting(key, default=None):
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO settings (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (key, str(value)),
        )
        conn.commit()


def add_quran_booking(name, contact, address, booking_date, booking_time, hours, rate_per_hour, notes=""):
    total = round(hours * rate_per_hour, 2)
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO quran_bookings
               (name, contact, address, booking_date, booking_time, hours, rate_per_hour, total_charge, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, contact, address, str(booking_date), str(booking_time), hours, rate_per_hour, total, notes,
             datetime.now().isoformat()),
        )
        conn.commit()
    return total


def add_grave_booking(name, contact, graveyard_address, service_date, service_time, quality, charge, notes=""):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO grave_bookings
               (name, contact, graveyard_address, service_date, service_time, quality, charge, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, contact, graveyard_address, str(service_date), str(service_time), quality, charge, notes,
             datetime.now().isoformat()),
        )
        conn.commit()


def get_all_quran_bookings():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM quran_bookings ORDER BY id DESC").fetchall()


def get_all_grave_bookings():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM grave_bookings ORDER BY id DESC").fetchall()


def update_status(table, booking_id, status):
    assert table in ("quran_bookings", "grave_bookings")
    with get_conn() as conn:
        conn.execute(f"UPDATE {table} SET status=? WHERE id=?", (status, booking_id))
        conn.commit()


def delete_booking(table, booking_id):
    assert table in ("quran_bookings", "grave_bookings")
    with get_conn() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id=?", (booking_id,))
        conn.commit()
