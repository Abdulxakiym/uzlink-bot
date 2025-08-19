import os
from pathlib import Path
import aiosqlite
from datetime import datetime
from .config import DB_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "models.sql"


async def init_db():
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        script = SCHEMA_FILE.read_text()
        await db.executescript(script)
        await db.commit()

async def get_db():
    return await aiosqlite.connect(DB_PATH)

async def fetch_user(user_id: int):
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if row:
            keys = [d[0] for d in cur.description]
            return dict(zip(keys, row))
        return None

async def fetch_driver(user_id: int):
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM drivers WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if row:
            keys = [d[0] for d in cur.description]
            return dict(zip(keys, row))
        return None

async def fetch_orders_for_user(user_id: int, role: str, limit: int = 10):
    column = "consumer_id" if role == "consumer" else "driver_id"
    async with await get_db() as db:
        cur = await db.execute(
            f"SELECT id, from_place, to_place, status FROM orders WHERE {column}=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cur.fetchall()
        keys = [d[0] for d in cur.description]
        return [dict(zip(keys, r)) for r in rows]

async def upsert_user(user_id: int, **fields):
    async with await get_db() as db:
        existing = await fetch_user(user_id)
        if existing:
            updates = ",".join(f"{k}=?" for k in fields)
            params = list(fields.values()) + [user_id]
            await db.execute(f"UPDATE users SET {updates} WHERE user_id=?", params)
        else:
            columns = ",".join(["user_id"] + list(fields.keys()))
            placeholders = ",".join(["?"] * (1 + len(fields)))
            params = [user_id] + list(fields.values())
            await db.execute(
                f"INSERT INTO users({columns}, created_at) VALUES({placeholders}, ?)",
                params + [datetime.utcnow().isoformat()],
            )
        await db.commit()

async def upsert_driver(user_id: int, **fields):
    async with await get_db() as db:
        cur = await db.execute("SELECT user_id FROM drivers WHERE user_id=?", (user_id,))
        exists = await cur.fetchone()
        if exists:
            updates = ",".join(f"{k}=?" for k in fields)
            params = list(fields.values()) + [user_id]
            await db.execute(f"UPDATE drivers SET {updates} WHERE user_id=?", params)
        else:
            columns = ",".join(["user_id"] + list(fields.keys()))
            placeholders = ",".join(["?"] * (1 + len(fields)))
            params = [user_id] + list(fields.values())
            await db.execute(
                f"INSERT INTO drivers({columns}) VALUES({placeholders})",
                params,
            )
        await db.commit()

async def set_driver_settings(user_id: int, **fields):
    async with await get_db() as db:
        cur = await db.execute("SELECT user_id FROM driver_settings WHERE user_id=?", (user_id,))
        exists = await cur.fetchone()
        if exists:
            updates = ",".join(f"{k}=?" for k in fields)
            params = list(fields.values()) + [user_id]
            await db.execute(f"UPDATE driver_settings SET {updates} WHERE user_id=?", params)
        else:
            columns = ",".join(["user_id"] + list(fields.keys()))
            placeholders = ",".join(["?"] * (1 + len(fields)))
            params = [user_id] + list(fields.values())
            await db.execute(
                f"INSERT INTO driver_settings({columns}) VALUES({placeholders})",
                params,
            )
        await db.commit()

async def create_order(**fields):
    async with await get_db() as db:
        columns = ",".join(fields.keys())
        placeholders = ",".join(["?"] * len(fields))
        params = list(fields.values())
        await db.execute(
            f"INSERT INTO orders({columns}, created_at, status) VALUES({placeholders}, ?, 'open')",
            params + [datetime.utcnow().isoformat()],
        )
        await db.commit()
        cur = await db.execute("SELECT last_insert_rowid()")
        rowid = (await cur.fetchone())[0]
        return rowid

async def fetch_open_orders():
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM orders WHERE status='open'")
        rows = await cur.fetchall()
        keys = [d[0] for d in cur.description]
        return [dict(zip(keys, r)) for r in rows]

async def fetch_order(order_id: int):
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = await cur.fetchone()
        if row:
            keys = [d[0] for d in cur.description]
            return dict(zip(keys, row))
        return None

async def assign_order(order_id: int, driver_id: int) -> bool:
    async with await get_db() as db:
        cur = await db.execute(
            "UPDATE orders SET status='accepted', driver_id=? WHERE id=? AND status='open'",
            (driver_id, order_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def update_order(order_id: int, **fields):
    async with await get_db() as db:
        updates = ",".join(f"{k}=?" for k in fields)
        params = list(fields.values()) + [order_id]
        await db.execute(f"UPDATE orders SET {updates} WHERE id=?", params)
        await db.commit()

async def log_event(order_id: int, event: str):
    async with await get_db() as db:
        await db.execute(
            "INSERT INTO order_events(order_id, ts, event) VALUES(?, ?, ?)",
            (order_id, datetime.utcnow().isoformat(), event),
        )
        await db.commit()

async def save_support_msg(user_id: int, kind: str, text: str):
    async with await get_db() as db:
        await db.execute(
            "INSERT INTO support_msgs(user_id, kind, text, created_at) VALUES(?, ?, ?, ?)",
            (user_id, kind, text, datetime.utcnow().isoformat()),
        )
        await db.commit()
