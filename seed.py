import sqlite3

from db import (
    add_product, add_customer, place_order, get_all_products,
    get_order_report, get_revenue_by_category, get_orders_between,
)

print("ADDING PRODUCTS...")
add_product("Air Force 1", "Sneakers", 42, 45000, 10)
add_product("Air Force 1", "Sneakers", 43, 45000, 6)
add_product("Puma Speedcat", "Sneakers", 43, 55000, 3)
add_product("Timberland Boots", "Boots", 44, 85000, 4)
add_product("Nike Slides", "Slides", 42, 20000, 8)

print("ADDING CUSTOMERS...")
ada = add_customer("Ada Obi", "08012345678", "Abuja")
tunde = add_customer("Tunde Bello", "08098765432", "Lagos")

print("PLACING ORDERS...")
order1 = place_order(ada, [(1, 2), (5, 1)])
order2 = place_order(tunde, [(4, 1)])
order3 = place_order(ada, [(2, 1), (3, 1)])

# Backdate two orders so the date-range report has something to filter
conn = sqlite3.connect("freykicks.db")
conn.execute("UPDATE orders SET order_date = '2026-10-20 10:00:00' WHERE id = ?", (order1,))
conn.execute("UPDATE orders SET order_date = '2026-10-28 15:30:00' WHERE id = ?", (order2,))
conn.commit()
conn.close()

print("\nTESTING A ROLLBACK (asking for more stock than exists)...")
stock_before = get_all_products()
try:
    place_order(tunde, [(5, 1), (4, 100)])   # the second item cannot be filled
except ValueError as error:
    print("Order refused:", error)
print("Stock unchanged after rollback:", stock_before == get_all_products())

print("\nORDER ITEMS (JOIN):")
for row in get_order_report():
    print(row)

print("\nREVENUE BY CATEGORY (SUM, COUNT, AVG):")
for row in get_revenue_by_category():
    print(row)

print("\nORDERS BETWEEN 2026-10-15 AND 2026-10-31 (DATE FILTER):")
for row in get_orders_between("2026-10-15", "2026-10-31"):
    print(row)