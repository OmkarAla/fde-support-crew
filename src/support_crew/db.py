"""SQLite order store used by the demo and by the tools."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .policy import Order

SEED: list[tuple[str, str, str, float, int, str, int]] = [
    ("ORD-1001", "Asha Rao", "Mechanical keyboard", 129.00, 12, "unused", 0),
    ("ORD-1002", "Vikram Shah", "Noise-cancelling headphones", 349.00, 9, "damaged", 0),
    ("ORD-1003", "Meera Iyer", "Office chair", 899.00, 20, "unused", 1),
    ("ORD-1004", "Rahul Menon", "USB-C dock", 89.00, 44, "unused", 0),
    ("ORD-1005", "Sana Khan", "Monitor", 219.00, 5, "used", 4),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer TEXT NOT NULL,
    item TEXT NOT NULL,
    amount REAL NOT NULL,
    delivered_days_ago INTEGER NOT NULL,
    condition TEXT NOT NULL,
    prior_refunds INTEGER NOT NULL
)
"""


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    return connection


def seed(connection: sqlite3.Connection) -> None:
    connection.executemany(
        "INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)",
        SEED,
    )
    connection.commit()


def get_order(connection: sqlite3.Connection, order_id: str) -> Order | None:
    row = connection.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()

    if row is None:
        return None

    return Order(
        order_id=row["order_id"],
        customer=row["customer"],
        item=row["item"],
        amount=row["amount"],
        delivered_days_ago=row["delivered_days_ago"],
        condition=row["condition"],
        prior_refunds=row["prior_refunds"],
    )
