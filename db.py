import sqlite3

# Rules shared by the whole program
CATEGORIES = ["Sneakers", "Cooperate", "Slides", "Canvas", "Formal"]
MIN_SIZE = 38
MAX_SIZE = 47

def connect_db():
    """Open a connection to the Frey Kicks database with foreign keys enforced."""
    conn = sqlite3.connect("freykicks.db")
    # SQLite only enforces foreign keys when this is turned on for each connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def add_product(name, category, size, price, stock):
    """Insert a new shoe into the products table.

    Category must be one of CATEGORIES (case does not matter).
    Returns the id of the new product.
    """
    # Match the category to the official spelling, or reject it
    matches = [c for c in CATEGORIES if c.lower() == category.lower()]
    if not matches:
        raise ValueError("Category must be one of: " + ", ".join(CATEGORIES))
    category = matches[0]

    conn = connect_db()
    try:
        cursor = conn.execute("""
            INSERT INTO products (name, category, size, price, stock)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, size, price, stock))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all_products():
    """Return every product as a list of rows."""
    conn = connect_db()
    try:
        cursor = conn.execute("SELECT * FROM products")
        return cursor.fetchall()
    finally:
        conn.close()


def search_products(category, size=None):
    """Search products by category, and optionally by size.

    The search ignores upper and lower case, so "sneakers" matches "Sneakers".
    Returns a list of matching rows (empty if nothing matches).
    """
    conn = connect_db()
    try:
        if size is None:
            cursor = conn.execute(
                "SELECT * FROM products WHERE category = ? COLLATE NOCASE",
                (category,)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM products "
                "WHERE category = ? COLLATE NOCASE AND size = ?",
                (category, size)
            )
        return cursor.fetchall()
    finally:
        conn.close()


def update_product(product_id, price, stock):
    """Change the price and stock of one product.

    Returns the number of rows changed (0 means no product has that id).
    """
    conn = connect_db()
    try:
        cursor = conn.execute("""
            UPDATE products
            SET price = ?, stock = ?
            WHERE id = ?
        """, (price, stock, product_id))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_product(product_id):
    """Delete a product by id.

    Returns the number of rows deleted (0 means no product has that id).
    Raises ValueError if the product appears in an order, because the
    database protects order history with a foreign key.
    """
    conn = connect_db()
    try:
        cursor = conn.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )
        conn.commit()
        return cursor.rowcount
    except sqlite3.IntegrityError:
        raise ValueError("This product is part of an order and cannot be deleted.")
    finally:
        conn.close()