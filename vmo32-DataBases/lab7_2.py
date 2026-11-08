from lab4_graphics_fixed import db_config

#!/usr/bin/env python3
"""
cinema_tickets_partition_50k.py

- Partitioned tickets table by show_date (RANGE by year)
- film_name column instead of purchaser
- Generates 50_000 sample tickets and inserts in batches
- Uses a global sequence for ticket_id and local PKs on partitions
- Uses psycopg2 + execute_values for fast bulk insert
"""

import os
import random
from datetime import date, datetime, timedelta
import psycopg2
from psycopg2 import sql
from psycopg2 import extras

# --- Настройки подключения (можно задать через env) ---
DB_PARAMS = db_config

NUM_RECORDS = 50_000
BATCH_SIZE = 5_000  # вставляем батчами

FILM_TITLES = [
    "The Last Horizon", "Midnight Café", "Семь нот счастья", "Galactic Run",
    "Забытый город", "Ocean's Whisper", "Paper Stars", "Ночная смена",
    "Echoes of Time", "The Red Seat", "Silent Alley", "Lucky Ticket"
]

def random_date(start_date: date, end_date: date) -> date:
    """Возвращает случайную дату между start_date и end_date (включительно)."""
    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))

def random_timestamp_between(start_dt: datetime, end_dt: datetime) -> datetime:
    delta = int((end_dt - start_dt).total_seconds())
    return start_dt + timedelta(seconds=random.randint(0, delta))

def generate_ticket_row():
    """Генератор одной тестовой строки (без ticket_id — выдаёт DB через sequence)."""
    # show_date между 2024-01-01 и 2027-12-31
    sd = random_date(date(2024, 1, 1), date(2027, 12, 31))
    show_id = random.randint(100, 400)  # id сеанса/зала/показа
    # seat: row A..O, number 1..30
    seat_row = chr(random.randint(ord('A'), ord('O')))
    seat_num = str(random.randint(1, 30))
    # цена: 6..15 евро/долл (пример)
    price = round(random.choice([6.0, 7.5, 8.5, 9.0, 10.0, 12.0, 15.0]), 2)
    # sold_at: случайная метка времени за последние 180 дней
    now = datetime.now()
    sold_at = random_timestamp_between(now - timedelta(days=180), now)
    film_name = random.choice(FILM_TITLES)
    return (show_id, seat_row, seat_num, price, sold_at, sd, film_name)

def ensure_schema_and_tables(conn):
    cur = conn.cursor()
    # Пересоздаём схему для повторяемости
    cur.execute("DROP SCHEMA IF EXISTS cinema CASCADE;")
    cur.execute("CREATE SCHEMA cinema;")

    # Sequence для глобальных ticket_id
    cur.execute("CREATE SEQUENCE cinema.ticket_id_seq START 1;")

    # Parent table без PK (чтобы не требовать partition key в PK)
    cur.execute("""
    CREATE TABLE cinema.tickets (
        ticket_id integer NOT NULL DEFAULT nextval('cinema.ticket_id_seq'),
        show_id    int         NOT NULL,
        seat_row   text,
        seat_num   text,
        price      numeric(8,2) NOT NULL,
        sold_at    timestamp with time zone NOT NULL DEFAULT now(),
        show_date  date        NOT NULL,
        film_name  text
    ) PARTITION BY RANGE (show_date);
    """)

    # Создаём партиции по годам 2024..2027 и DEFAULT для остального
    cur.execute("""
    CREATE TABLE cinema.tickets_2024 PARTITION OF cinema.tickets
        FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
    CREATE TABLE cinema.tickets_2025 PARTITION OF cinema.tickets
        FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
    CREATE TABLE cinema.tickets_2026 PARTITION OF cinema.tickets
        FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
    CREATE TABLE cinema.tickets_2027 PARTITION OF cinema.tickets
        FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
    CREATE TABLE cinema.tickets_future PARTITION OF cinema.tickets
        DEFAULT;
    """)

    # Добавим локальные PK на каждую партицию по ticket_id
    cur.execute("ALTER TABLE cinema.tickets_2024 ADD PRIMARY KEY (ticket_id);")
    cur.execute("ALTER TABLE cinema.tickets_2025 ADD PRIMARY KEY (ticket_id);")
    cur.execute("ALTER TABLE cinema.tickets_2026 ADD PRIMARY KEY (ticket_id);")
    cur.execute("ALTER TABLE cinema.tickets_2027 ADD PRIMARY KEY (ticket_id);")
    cur.execute("ALTER TABLE cinema.tickets_future ADD PRIMARY KEY (ticket_id);")

    # Индексы: на show_id и film_name для быстрого поиска по сеансу/фильму (создаём на партициях)
    cur.execute("CREATE INDEX ON cinema.tickets_2024 (show_id);")
    cur.execute("CREATE INDEX ON cinema.tickets_2025 (show_id);")
    cur.execute("CREATE INDEX ON cinema.tickets_2026 (show_id);")
    cur.execute("CREATE INDEX ON cinema.tickets_2027 (show_id);")
    cur.execute("CREATE INDEX ON cinema.tickets_future (show_id);")

    cur.execute("CREATE INDEX ON cinema.tickets_2024 (film_name);")
    cur.execute("CREATE INDEX ON cinema.tickets_2025 (film_name);")
    cur.execute("CREATE INDEX ON cinema.tickets_2026 (film_name);")
    cur.execute("CREATE INDEX ON cinema.tickets_2027 (film_name);")
    cur.execute("CREATE INDEX ON cinema.tickets_future (film_name);")

    conn.commit()
    cur.close()

def bulk_insert_random(conn, total=NUM_RECORDS, batch_size=BATCH_SIZE):
    cur = conn.cursor()
    insert_sql = """
    INSERT INTO cinema.tickets
      (show_id, seat_row, seat_num, price, sold_at, show_date, film_name)
    VALUES %s
    """
    inserted = 0
    while inserted < total:
        to_generate = min(batch_size, total - inserted)
        batch = [generate_ticket_row() for _ in range(to_generate)]
        # execute_values подставит множество строк эффективно
        extras.execute_values(cur, insert_sql, batch, template=None, page_size=1000)
        conn.commit()
        inserted += to_generate
        print(f"Inserted {inserted}/{total} rows...")
    cur.close()

def preview_counts(conn):
    cur = conn.cursor()
    print("\nCounts by partition:")
    for part in ["tickets_2024", "tickets_2025", "tickets_2026", "tickets_2027", "tickets_future"]:
        cur.execute(sql.SQL("SELECT count(*) FROM cinema.{}").format(sql.Identifier(part)))
        print(f"  {part}: {cur.fetchone()[0]}")
    cur.close()

def demo_explain(conn):
    cur = conn.cursor()
    print("\nEXPLAIN (FORMAT TEXT) for show_date BETWEEN 2025-01-01 and 2025-12-31 (expect pruning to tickets_2025):")
    cur.execute("EXPLAIN (FORMAT TEXT) SELECT count(*) FROM cinema.tickets WHERE show_date BETWEEN '2025-01-01' AND '2025-12-31';")
    for r in cur.fetchall():
        print(r[0])

    print("\nEXPLAIN (FORMAT TEXT) for search by film_name = 'The Last Horizon' (may scan multiple partitions):")
    cur.execute("EXPLAIN (FORMAT TEXT) SELECT * FROM cinema.tickets WHERE film_name = 'The Last Horizon' LIMIT 5;")
    for r in cur.fetchall():
        print(r[0])
    cur.close()

def main():
    print("Connecting to DB...")
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        print("Creating schema and partitioned table...")
        ensure_schema_and_tables(conn)

        print(f"Generating and inserting {NUM_RECORDS} records in batches of {BATCH_SIZE}...")
        bulk_insert_random(conn, total=NUM_RECORDS, batch_size=BATCH_SIZE)

        preview_counts(conn)
        demo_explain(conn)

        print("\nDone. Example quick check:")
        # покажем 5 случайных строк
        cur = conn.cursor()
        cur.execute("SELECT ticket_id, show_id, show_date, film_name, seat_row, seat_num, price FROM cinema.tickets ORDER BY random() LIMIT 5;")
        for r in cur.fetchall():
            print(" ", r)
        cur.close()

    finally:
        conn.close()

if __name__ == "__main__":
    main()

