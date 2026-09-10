"""
db.py — SQLite backend for Qur'an Khuwani Service
Handles storage for:
  - User accounts (signup / login)
  - Qur'an Khuwani appointment bookings
  - Grave Renovation Service bookings
  - Admin-editable pricing settings
"""

import sqlite3
import hashlib
import os
import binascii
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


def _ensure_column(conn, table, column, coltype):
    """Add a column to an existing table if it doesn't already exist (simple migration)."""
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS quran_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
                user_id INTEGER,
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

        # migrate older DBs that predate the users table / user_id columns
        _ensure_column(conn, "quran_bookings", "user_id", "INTEGER")
        _ensure_column(conn, "grave_bookings", "user_id", "INTEGER")

        defaults = {
            "quran_default_rate": "500",
            "grave_normal_price": "3000",
            "grave_good_price": "6000",
            "grave_renew_price": "10000",
        }
        for k, v in defaults.items():
            cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        conn.commit()


# ------------------------------------------------------------- settings --
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


# ------------------------------------------------------------------ auth --
def _hash_password(password, salt_hex=None):
    if salt_hex is None:
        salt = os.urandom(16)
    else:
        salt = binascii.unhexlify(salt_hex)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return binascii.hexlify(pwd_hash).decode(), binascii.hexlify(salt).decode()


def create_user(username, email, password):
    """Returns (True, user_dict) on success, or (False, error_message) on failure."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."
    with get_conn() as conn:
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            return False, "That username is already taken."
        pwd_hash, salt = _hash_password(password)
        cur = conn.execute(
            """INSERT INTO users (username, email, password_hash, salt, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (username, email.strip(), pwd_hash, salt, datetime.now().isoformat()),
        )
        conn.commit()
        return True, {"id": cur.lastrowid, "username": username, "email": email}


def authenticate_user(username, password):
    """Returns user dict on success, None on failure."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=?", (username.strip(),)).fetchone()
        if not row:
            return None
        computed_hash, _ = _hash_password(password, row["salt"])
        if computed_hash == row["password_hash"]:
            return {"id": row["id"], "username": row["username"], "email": row["email"]}
        return None


# -------------------------------------------------------------- bookings --
def add_quran_booking(name, contact, address, booking_date, booking_time, hours, rate_per_hour,
                       notes="", user_id=None):
    total = round(hours * rate_per_hour, 2)
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO quran_bookings
               (user_id, name, contact, address, booking_date, booking_time, hours, rate_per_hour,
                total_charge, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, contact, address, str(booking_date), str(booking_time), hours, rate_per_hour,
             total, notes, datetime.now().isoformat()),
        )
        conn.commit()
    return total


def add_grave_booking(name, contact, graveyard_address, service_date, service_time, quality, charge,
                       notes="", user_id=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO grave_bookings
               (user_id, name, contact, graveyard_address, service_date, service_time, quality, charge,
                notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, contact, graveyard_address, str(service_date), str(service_time), quality,
             charge, notes, datetime.now().isoformat()),
        )
        conn.commit()


def get_all_quran_bookings():
    with get_conn() as conn:
        return conn.execute("""
            SELECT qb.*, u.username AS booked_by
            FROM quran_bookings qb
            LEFT JOIN users u ON u.id = qb.user_id
            ORDER BY qb.id DESC
        """).fetchall()


def get_all_grave_bookings():
    with get_conn() as conn:
        return conn.execute("""
            SELECT gb.*, u.username AS booked_by
            FROM grave_bookings gb
            LEFT JOIN users u ON u.id = gb.user_id
            ORDER BY gb.id DESC
        """).fetchall()


def get_user_quran_bookings(user_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM quran_bookings WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()


def get_user_grave_bookings(user_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM grave_bookings WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()


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
