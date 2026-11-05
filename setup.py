import sqlite3

# Connect to the database file (it is created if it doesn't exist yet)
conn = sqlite3.connect("freykicks.db")

# SQLite does not enforce foreign keys unless this is turned on
conn.execute("PRAGMA foreign_keys = ON")

# Products: one row per shoe per size, each with its own stock
conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL COLLATE NOCASE,
        category TEXT NOT NULL,
        price INTEGER NOT NULL CHECK (price >= 0),      -- whole Naira
        size INTEGER NOT NULL CHECK (size BETWEEN 38 AND 47),
        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
        UNIQUE (name, size)                             -- same name allowed, but not in the same size
    )
""")

# Customers: phone numbers must be unique
conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        location TEXT
    )
""")

# Orders: each order belongs to one customer
conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        status TEXT NOT NULL DEFAULT 'Pending'
            CHECK (status IN ('Pending', 'Completed', 'Cancelled')),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
""")

# Order items: links an order to the products in it
# price_at_sale keeps the price at the time of purchase, so old orders
# stay correct if a product's price changes later
conn.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        price_at_sale INTEGER NOT NULL CHECK (price_at_sale >= 0),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")

# Audit log: every stock change is recorded automatically by a trigger.
# product_id has no foreign key on purpose, so history never blocks deleting a product.
conn.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity_change INTEGER NOT NULL,
        new_stock INTEGER NOT NULL,
        moved_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    )
""")

conn.execute("""
    CREATE TRIGGER IF NOT EXISTS log_stock_change
    AFTER UPDATE OF stock ON products
    WHEN NEW.stock != OLD.stock
    BEGIN
        INSERT INTO stock_movements (product_id, quantity_change, new_stock)
        VALUES (NEW.id, NEW.stock - OLD.stock, NEW.stock);
    END
""")

conn.commit()
conn.close()
print("Database and all tables created.")