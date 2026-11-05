import sqlite3

# Connect to the database file (it is created if it doesn't exist yet)
conn = sqlite3.connect("freykicks.db")

# SQLite does not enforce foreign keys unless this is turned on
conn.execute("PRAGMA foreign_keys = ON")

# Create the products table
conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price INTEGER NOT NULL CHECK (price >= 0),
        size TEXT NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
    )
""")

# Create customers table
conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        location TEXT
    )
""")

# Create orders table
conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed', 'Cancelled')),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
""")

# Create order_items table
conn.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        price_at_sale INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")


conn.commit()
conn.close()
print("Database and all table created.")