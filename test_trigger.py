import time

from db import (
    add_product, update_product, place_order,
    get_all_products, get_all_customers, get_stock_movements,
)

# A unique name so the test can be run many times
name = f"Trigger Test {int(time.time())}"
product_id = add_product(name, "Sneakers", 40, 30000, 10)

def log_for_product():
    """Return the log rows for the test product, oldest first."""
    rows = [r for r in get_stock_movements() if r[1] == name]
    return list(reversed(rows))

# Test 1: changing stock through update_product is logged
update_product(product_id, 30000, 7)          # 10 -> 7, so the change is -3
log = log_for_product()
print("Test 1 (stock change logged):",
      "PASS" if len(log) == 1 and log[0][3] == -3 and log[0][4] == 7 else "FAIL", log)

# Test 2: changing only the price does NOT create a log row
update_product(product_id, 35000, 7)
print("Test 2 (price-only change not logged):",
      "PASS" if len(log_for_product()) == 1 else "FAIL")

# Test 3: placing an order reduces stock and is logged
customers = get_all_customers()
if customers:
    place_order(customers[0][0], [(product_id, 2)])   # 7 -> 5
    log = log_for_product()
    print("Test 3 (order logged):",
          "PASS" if len(log) == 2 and log[1][3] == -2 and log[1][4] == 5 else "FAIL", log)

    # Test 4: a failed order is rolled back, and so is its log row
    try:
        place_order(customers[0][0], [(product_id, 100)])   # more than the stock
    except ValueError as error:
        print("Order refused:", error)
    print("Test 4 (failed order leaves no log):",
          "PASS" if len(log_for_product()) == 2 else "FAIL")
else:
    print("Tests 3 and 4 skipped: add a customer first (menu option 6).")