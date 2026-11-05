import sqlite3

# Rules shared by the whole program
CATEGORIES = ["Sneakers", "Boots", "Slides", "Sandals", "Formal"]
MIN_SIZE = 38
MAX_SIZE = 47


def connect_db():
    """Open a connection to the Frey Kicks database with foreign keys enforced."""
    conn = sqlite3.connect("freykicks.db")
    # SQLite only enforces foreign keys when this is turned on for each connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------- products

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
            INSERT INTO products (name, category, price, size, stock)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, size, stock))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_products():
    """Return every product as a list of rows (id, name, category, price, size, stock)."""
    conn = connect_db()
    try:
        cursor = conn.execute(
            "SELECT id, name, category, price, size, stock FROM products"
        )
        return cursor.fetchall()
    finally:
        conn.close()


def search_products(category, size=None):
    """Search products by category, and optionally by size.

    The search ignores upper and lower case.
    Returns a list of matching rows (empty if nothing matches).
    """
    conn = connect_db()
    try:
        sql = ("SELECT id, name, category, price, size, stock FROM products "
               "WHERE category = ? COLLATE NOCASE")
        params = [category]
        if size is not None:
            sql += " AND size = ?"
            params.append(size)
        return conn.execute(sql, params).fetchall()
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
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount
    except sqlite3.IntegrityError:
        raise ValueError("This product is part of an order and cannot be deleted.")
    finally:
        conn.close()


# --------------------------------------------------------------- customers

def add_customer(name, phone, location=None):
    """Insert a new customer and return the new customer's id.

    Raises ValueError for an empty name, a phone number that is not
    10 to 15 digits (an optional leading + is allowed), or a phone
    number that already belongs to another customer.
    """
    name = name.strip()
    phone = phone.strip()
    location = location.strip() if location else None

    if not name:
        raise ValueError("Customer name cannot be empty.")

    digits = phone[1:] if phone.startswith("+") else phone
    if not digits.isdigit() or not 10 <= len(digits) <= 15:
        raise ValueError("Phone must be 10 to 15 digits (a leading + is allowed).")

    conn = connect_db()
    try:
        cursor = conn.execute(
            "INSERT INTO customers (name, phone, location) VALUES (?, ?, ?)",
            (name, phone, location or None),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("A customer with this phone number already exists.")
    finally:
        conn.close()


def get_all_customers():
    """Return every customer as a list of rows (id, name, phone, location)."""
    conn = connect_db()
    try:
        return conn.execute(
            "SELECT id, name, phone, location FROM customers"
        ).fetchall()
    finally:
        conn.close()


# ------------------------------------------------------------------ orders

def place_order(customer_id, items):
    """Place an order inside one transaction.

    items is a list of (product_id, quantity) pairs.
    Steps: create the order, then for each item check stock, record the
    item at the product's current price, and reduce stock. If anything
    fails (unknown customer or product, not enough stock), the whole
    order is rolled back so no half-finished order is saved.

    Returns the new order's id. Raises ValueError with a readable message.
    """
    if not items:
        raise ValueError("An order must contain at least one item.")

    conn = connect_db()
    try:
        customer = conn.execute(
            "SELECT id FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if customer is None:
            raise ValueError("Customer not found.")

        cursor = conn.execute(
            "INSERT INTO orders (customer_id) VALUES (?)", (customer_id,)
        )
        order_id = cursor.lastrowid

        for product_id, quantity in items:
            if quantity <= 0:
                raise ValueError("Quantity must be at least 1.")

            product = conn.execute(
                "SELECT name, size, price, stock FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} not found.")

            name, size, price, stock = product
            if stock < quantity:
                raise ValueError(
                    f"Not enough stock for {name} (size {size}): "
                    f"{stock} left, {quantity} requested."
                )

            # Save the current price so later price changes do not alter this order
            conn.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_sale)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))

            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, product_id),
            )

        conn.commit()
        return order_id

    except Exception:
        # Undo everything done so far in this order
        conn.rollback()
        raise
    finally:
        conn.close()


# ----------------------------------------------------------------- reports

def get_order_report():
    """JOIN report: one row per item bought, across four tables.

    Returns rows of (order_id, order_date, customer, product, size,
    quantity, price_at_sale, line_total).
    """
    conn = connect_db()
    try:
        return conn.execute("""
            SELECT o.id, o.order_date, c.name, p.name, p.size,
                   oi.quantity, oi.price_at_sale,
                   oi.quantity * oi.price_at_sale AS line_total
            FROM orders o
            JOIN customers c   ON o.customer_id = c.id
            JOIN order_items oi ON oi.order_id = o.id
            JOIN products p    ON oi.product_id = p.id
            ORDER BY o.id, p.name
        """).fetchall()
    finally:
        conn.close()


def get_revenue_by_category():
    """Aggregate report using COUNT, SUM, and AVG, grouped by category.

    Cancelled orders are left out.
    Returns rows of (category, number_of_orders, pairs_sold,
    total_revenue, average_price).
    """
    conn = connect_db()
    try:
        return conn.execute("""
            SELECT p.category,
                   COUNT(DISTINCT o.id)               AS orders_count,
                   SUM(oi.quantity)                   AS pairs_sold,
                   SUM(oi.quantity * oi.price_at_sale) AS revenue,
                   AVG(oi.price_at_sale)              AS avg_price
            FROM order_items oi
            JOIN orders o   ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status != 'Cancelled'
            GROUP BY p.category
            ORDER BY revenue DESC
        """).fetchall()
    finally:
        conn.close()


def get_orders_between(start_date, end_date):
    """Date-range report: orders placed from start_date to end_date, inclusive.

    Dates are 'YYYY-MM-DD' text. Returns rows of
    (order_id, order_date, customer, status, order_total).
    """
    conn = connect_db()
    try:
        return conn.execute("""
            SELECT o.id, o.order_date, c.name, o.status,
                   SUM(oi.quantity * oi.price_at_sale) AS order_total
            FROM orders o
            JOIN customers c    ON o.customer_id = c.id
            JOIN order_items oi ON oi.order_id = o.id
            WHERE date(o.order_date) BETWEEN ? AND ?
            GROUP BY o.id
            ORDER BY o.order_date
        """, (start_date, end_date)).fetchall()
    finally:
        conn.close()

def get_stock_movements():
    """Return the stock change log, newest first: (id, product, size, change, new_stock, time)."""
    conn = connect_db()
    try:
        return conn.execute("""
            SELECT m.id, p.name, p.size, m.quantity_change, m.new_stock, m.moved_at
            FROM stock_movements m
            JOIN products p ON m.product_id = p.id
            ORDER BY m.id DESC
        """).fetchall()
    finally:
        conn.close()