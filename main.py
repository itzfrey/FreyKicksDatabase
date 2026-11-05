import sqlite3
from datetime import datetime

from db import (
    CATEGORIES,
    MIN_SIZE,
    MAX_SIZE,
    add_product,
    get_all_products,
    search_products,
    update_product,
    delete_product,
    add_customer,
    get_all_customers,
    place_order,
    get_order_report,
    get_revenue_by_category,
    get_orders_between,
)


def show_menu():
    """Print the main menu."""
    print("\n================================")
    print("          FREY KICKS")
    print("     INVENTORY MANAGEMENT")
    print("================================")
    print("1.  Add Product")
    print("2.  View All Products")
    print("3.  Search Products")
    print("4.  Update Product")
    print("5.  Delete Product")
    print("6.  Add Customer")
    print("7.  View Customers")
    print("8.  Place Order")
    print("9.  Report: All Order Items")
    print("10. Report: Revenue by Category")
    print("11. Report: Orders Between Dates")
    print("0.  Quit")
    print("================================")


# ------------------------------------------------------------ input helpers

def ask_category():
    """Show the allowed categories and keep asking until a valid one is entered.

    Returns the category with its official capitalization.
    """
    while True:
        print("Categories: " + ", ".join(CATEGORIES))
        entry = input("Enter category: ").strip()
        for category in CATEGORIES:
            if entry.lower() == category.lower():
                return category
        print("Invalid category. Please choose one from the list.")


def ask_size():
    """Keep asking until the user enters a whole-number size in the allowed range."""
    while True:
        entry = input(f"Enter shoe size ({MIN_SIZE}-{MAX_SIZE}): ").strip()
        if entry.isdigit() and MIN_SIZE <= int(entry) <= MAX_SIZE:
            return int(entry)
        print(f"Invalid size. Use a whole number from {MIN_SIZE} to {MAX_SIZE}.")


def ask_int(prompt, minimum=0):
    """Keep asking until the user enters a whole number of at least `minimum`."""
    while True:
        entry = input(prompt).strip()
        if entry.isdigit() and int(entry) >= minimum:
            return int(entry)
        print(f"Please enter a whole number of {minimum} or more.")


def ask_date(prompt):
    """Keep asking until the user enters a real date as YYYY-MM-DD."""
    while True:
        entry = input(prompt).strip()
        try:
            datetime.strptime(entry, "%Y-%m-%d")
            return entry
        except ValueError:
            print("Invalid date. Use the format YYYY-MM-DD, for example 2026-11-05.")


# --------------------------------------------------------- display helpers

def display_products(products):
    """Print product rows (id, name, category, price, size, stock) with labels."""
    if not products:
        print("No products found.")
        return

    for product in products:
        print("--------------------------------")
        print(f"Product ID: {product[0]}")
        print(f"Name:       {product[1]}")
        print(f"Category:   {product[2]}")
        print(f"Price:      ₦{product[3]:,}")
        print(f"Size:       {product[4]}")
        print(f"Stock:      {product[5]}")
    print("--------------------------------")


def display_customers(customers):
    """Print customer rows (id, name, phone, location) with labels."""
    if not customers:
        print("No customers found.")
        return

    for customer in customers:
        print("--------------------------------")
        print(f"Customer ID: {customer[0]}")
        print(f"Name:        {customer[1]}")
        print(f"Phone:       {customer[2]}")
        print(f"Location:    {customer[3] or 'Not given'}")
    print("--------------------------------")


def display_order_report(rows):
    """Print the joined order report, one block per item bought."""
    if not rows:
        print("No orders found.")
        return

    for row in rows:
        print("--------------------------------")
        print(f"Order #{row[0]}  ({row[1]})")
        print(f"Customer:  {row[2]}")
        print(f"Product:   {row[3]} (size {row[4]})")
        print(f"Quantity:  {row[5]} x ₦{row[6]:,} = ₦{row[7]:,}")
    print("--------------------------------")


def display_revenue_report(rows):
    """Print the revenue-by-category summary."""
    if not rows:
        print("No sales found.")
        return

    for row in rows:
        print("--------------------------------")
        print(f"Category:      {row[0]}")
        print(f"Orders:        {row[1]}")
        print(f"Pairs sold:    {row[2]}")
        print(f"Revenue:       ₦{row[3]:,}")
        print(f"Average price: ₦{row[4]:,.0f}")
    print("--------------------------------")


def display_orders_between(rows):
    """Print the orders found in a date range."""
    if not rows:
        print("No orders in that date range.")
        return

    for row in rows:
        print("--------------------------------")
        print(f"Order #{row[0]}  ({row[1]})")
        print(f"Customer: {row[2]}")
        print(f"Status:   {row[3]}")
        print(f"Total:    ₦{row[4]:,}")
    print("--------------------------------")


# ---------------------------------------------------------------- handlers

def handle_add_product():
    """Ask for product details and add the product."""
    name = input("Enter product name: ").strip()

    # An empty string would pass NOT NULL, so check for it here
    if not name:
        print("Name cannot be empty.")
        return

    category = ask_category()
    size = ask_size()
    price = ask_int("Enter price: ")
    stock = ask_int("Enter stock quantity: ")

    try:
        add_product(name, category, size, price, stock)
        print("Product added successfully!")
    except sqlite3.IntegrityError:
        # Either a CHECK constraint failed or this name and size already exist
        print("The database rejected this product. It may already exist "
              "in that size. Use Update Product to change its stock.")
    except ValueError as error:
        print(error)


def handle_update_product():
    """Ask for a product id with new price and stock, then update it."""
    product_id = ask_int("Enter product ID: ")
    price = ask_int("Enter new price: ")
    stock = ask_int("Enter new stock quantity: ")

    if update_product(product_id, price, stock):
        print("Product updated successfully!")
    else:
        print("No product found with that ID.")


def handle_delete_product():
    """Ask for a product id and delete it if it has no orders."""
    product_id = ask_int("Enter product ID to delete: ")

    try:
        if delete_product(product_id):
            print("Product deleted successfully!")
        else:
            print("No product found with that ID.")
    except ValueError as error:
        # Raised by delete_product when the product is part of an order
        print(error)


def handle_add_customer():
    """Ask for customer details and add the customer."""
    name = input("Enter customer name: ").strip()
    phone = input("Enter phone number: ").strip()
    location = input("Enter location (optional, press Enter to skip): ").strip()

    try:
        customer_id = add_customer(name, phone, location)
        print(f"Customer added successfully! Customer ID: {customer_id}")
    except ValueError as error:
        print(error)


def handle_place_order():
    """Collect a customer and a list of items, then place the order."""
    customers = get_all_customers()
    if not customers:
        print("Add a customer first.")
        return

    display_customers(customers)
    customer_id = ask_int("Enter customer ID: ")

    products = get_all_products()
    display_products(products)
    names = {p[0]: f"{p[1]} (size {p[4]})" for p in products}

    cart = {}  # product id -> quantity; a repeated product adds to its quantity
    while True:
        entry = input("\nEnter product ID to add (press Enter when done): ").strip()
        if entry == "":
            break
        if not entry.isdigit() or int(entry) not in names:
            print("No product with that ID. Check the list above.")
            continue

        quantity = ask_int("Enter quantity: ", minimum=1)
        product_id = int(entry)
        cart[product_id] = cart.get(product_id, 0) + quantity

        # Show the order so far, so it is clear the item was added
        print("Order so far:")
        for pid, qty in cart.items():
            print(f"  {qty} x {names[pid]}")

    if not cart:
        print("No items added. Order cancelled.")
        return

    try:
        order_id = place_order(customer_id, list(cart.items()))
        print(f"Order #{order_id} placed successfully!")
    except ValueError as error:
        # The order was rolled back, so nothing was saved
        print(f"Order not placed: {error}")

def handle_orders_between():
    """Ask for two dates and show the orders placed between them."""
    start_date = ask_date("Enter start date (YYYY-MM-DD): ")
    end_date = ask_date("Enter end date (YYYY-MM-DD): ")

    if start_date > end_date:
        print("The start date must not be after the end date.")
        return

    display_orders_between(get_orders_between(start_date, end_date))


def main():
    """Run the menu until the user chooses to quit."""
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            handle_add_product()
        elif choice == "2":
            print("\nALL PRODUCTS")
            display_products(get_all_products())
        elif choice == "3":
            display_products(search_products(ask_category()))
        elif choice == "4":
            handle_update_product()
        elif choice == "5":
            handle_delete_product()
        elif choice == "6":
            handle_add_customer()
        elif choice == "7":
            print("\nALL CUSTOMERS")
            display_customers(get_all_customers())
        elif choice == "8":
            handle_place_order()
        elif choice == "9":
            print("\nALL ORDER ITEMS")
            display_order_report(get_order_report())
        elif choice == "10":
            print("\nREVENUE BY CATEGORY")
            display_revenue_report(get_revenue_by_category())
        elif choice == "11":
            handle_orders_between()
        elif choice == "0":
            print("Thank you for using Frey Kicks Inventory System!")
            break
        else:
            print("Invalid choice. Please select an option from the menu.")


# Only start the menu when this file is run directly
if __name__ == "__main__":
    main()