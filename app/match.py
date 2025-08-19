from typing import List, Dict
from haversine import haversine
from .config import RADIUS_KM
from .db import get_db


async def drivers_for_order(order: Dict) -> List[int]:
    """Return driver ids suitable for given order."""
    async with await get_db() as db:
        cur = await db.execute(
            """SELECT u.user_id, d.car_capacity_kg, d.car_body, s.mode, s.lat, s.lon
               FROM users u
               JOIN drivers d ON u.user_id = d.user_id
               LEFT JOIN driver_settings s ON u.user_id = s.user_id
               WHERE u.role='driver'""",
        )
        drivers = await cur.fetchall()
    ids: List[int] = []
    for row in drivers:
        user_id, capacity, body, mode, lat, lon = row
        if capacity and capacity < order.get("weight_kg", 0):
            continue
        if order.get("body_type") and body and order["body_type"].lower() not in body.lower():
            continue
        if (
            mode == "nearby"
            and lat and lon
            and order.get("consumer_load_lat") and order.get("consumer_load_lon")
        ):
            distance = haversine(
                (lat, lon),
                (order["consumer_load_lat"], order["consumer_load_lon"]),
            )
            if distance > RADIUS_KM:
                continue
        ids.append(user_id)
    return ids


async def orders_for_driver(user_id: int) -> List[Dict]:
    async with await get_db() as db:
        cur = await db.execute(
            "SELECT car_capacity_kg, car_body FROM drivers WHERE user_id=?",
            (user_id,),
        )
        driver = await cur.fetchone()
        capacity, body = driver if driver else (None, None)
        cur = await db.execute(
            "SELECT mode, lat, lon FROM driver_settings WHERE user_id=?",
            (user_id,),
        )
        settings = await cur.fetchone()
        mode, lat, lon = settings if settings else ("all", None, None)
        cur = await db.execute("SELECT * FROM orders WHERE status='open'")
        rows = await cur.fetchall()
        keys = [d[0] for d in cur.description]
        result: List[Dict] = []
        for r in rows:
            od = dict(zip(keys, r))
            if capacity and od.get("weight_kg") and od["weight_kg"] > capacity:
                continue
            if od.get("body_type") and body and od["body_type"].lower() not in body.lower():
                continue
            if (
                mode == "nearby"
                and lat and lon
                and od.get("consumer_load_lat") and od.get("consumer_load_lon")
            ):
                dist = haversine(
                    (lat, lon),
                    (od["consumer_load_lat"], od["consumer_load_lon"]),
                )
                if dist > RADIUS_KM:
                    continue
            result.append(od)
        return result

