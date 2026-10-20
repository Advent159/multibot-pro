# =====================================================================
# MultiBot Pro - Database Module (SQLite)
# =====================================================================
import sqlite3
import os
from datetime import datetime
import sys

# Add parent dir ke path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import DATABASE_PATH


def get_connection():
    """Bikin koneksi ke SQLite. Auto-create folder kalau belum ada."""
    db_path = os.path.abspath(DATABASE_PATH)
    db_dir = os.path.dirname(db_path)

    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Folder dibuat: {db_dir}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Inisialisasi tabel-tabel yang dibutuhkan."""
    conn = get_connection()
    cursor = conn.cursor()

    # ============ TABLE: USERS ============
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            display_name TEXT,
            server_name TEXT,
            points INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ============ TABLE: GAME_HISTORY ============
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            game_type TEXT,
            result TEXT,
            points_change INTEGER,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def get_user(user_id):
    """Ambil data user. Kalau belum ada, buat baru."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (str(user_id), "Unknown")
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        user = cursor.fetchone()

    conn.close()
    return dict(user) if user else None


def update_user(user_id, **kwargs):
    """Update data user. Contoh: update_user(id, points=100)"""
    if not kwargs:
        return

    conn = get_connection()
    cursor = conn.cursor()

    get_user(user_id)  # pastikan ada

    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [str(user_id)]

    cursor.execute(f"UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", values)
    conn.commit()
    conn.close()


def update_user_info(user_id, username=None, display_name=None, server_name=None):
    """Update info user Discord di database."""
    conn = get_connection()
    cursor = conn.cursor()

    get_user(user_id)  # pastikan ada

    updates = []
    values = []

    if username:
        updates.append("username = ?")
        values.append(username)
    if display_name:
        updates.append("display_name = ?")
        values.append(display_name)
    if server_name:
        updates.append("server_name = ?")
        values.append(server_name)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(str(user_id))
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        cursor.execute(query, values)
        conn.commit()

    conn.close()


def add_points(user_id, amount, game_type="manual", result=""):
    """Tambah/kurangi poin user."""
    conn = get_connection()
    cursor = conn.cursor()

    user = get_user(user_id)
    new_points = max(0, user["points"] + amount)

    cursor.execute(
        "UPDATE users SET points = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (new_points, str(user_id))
    )

    cursor.execute(
        "INSERT INTO game_history (user_id, game_type, result, points_change) VALUES (?, ?, ?, ?)",
        (str(user_id), game_type, result, amount)
    )

    conn.commit()
    conn.close()
    return new_points


def record_game(user_id, won):
    """Catat game played & won/lost."""
    conn = get_connection()
    cursor = conn.cursor()

    get_user(user_id)

    if won:
        cursor.execute(
            """UPDATE users
               SET games_played = games_played + 1,
                   games_won = games_won + 1,
                   updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (str(user_id),)
        )
    else:
        cursor.execute(
            """UPDATE users
               SET games_played = games_played + 1,
                   games_lost = games_lost + 1,
                   updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (str(user_id),)
        )

    conn.commit()
    conn.close()


def get_leaderboard(limit=10):
    """Ambil top users by points."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, display_name, points, games_played, games_won FROM users ORDER BY points DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats(user_id):
    """Ambil statistik user."""
    return get_user(user_id)


if __name__ == "__main__":
    init_database()
    print("\n📊 Test database:")
    print("=" * 60)

    user = get_user("123456")
    print(f"User: {user}")

    update_user_info("123456", username="alek", display_name="Just call me Alek.", server_name="Sekte Titik Koma")
    add_points("123456", 50, "test", "won")
    record_game("123456", won=True)

    user = get_user("123456")
    print(f"After update: {user}")

    print(f"\nLeaderboard:")
    for u in get_leaderboard(5):
        print(f"  {u['username']}: {u['points']} pts")