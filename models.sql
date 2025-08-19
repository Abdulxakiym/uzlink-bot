CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    role TEXT,
    lang TEXT,
    full_name TEXT,
    dob TEXT,
    phone TEXT,
    selfie_file_id TEXT,
    id_file_id TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS drivers(
    user_id INTEGER PRIMARY KEY,
    exp_years INTEGER,
    car_brand TEXT,
    car_year INTEGER,
    car_capacity_kg INTEGER,
    car_body TEXT
);

CREATE TABLE IF NOT EXISTS driver_settings(
    user_id INTEGER PRIMARY KEY,
    mode TEXT,
    radius_km INTEGER,
    lat REAL,
    lon REAL
);

CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consumer_id INTEGER,
    from_place TEXT,
    to_place TEXT,
    load_date TEXT,
    load_time TEXT,
    ship_date TEXT,
    ship_time TEXT,
    weight_kg INTEGER,
    body_type TEXT,
    status TEXT,
    driver_id INTEGER,
    consumer_load_lat REAL,
    consumer_load_lon REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS order_events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    ts TEXT,
    event TEXT
);

CREATE TABLE IF NOT EXISTS support_msgs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    kind TEXT,
    text TEXT,
    created_at TEXT
);
