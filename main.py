import sqlite3

from db import (
    CATEGORIES,
    MIN_SIZE,
    MAX_SIZE,
    add_product,
    get_all_products,
    search_products,
    update_product,
    delete_product
)


def show_menu():
    """Print the main menu."""
    print("\n================================")
    print("          FREY KICKS")
    print("     INVENTORY MANAGEMENT")
    print("================================")
    print("1. Add Product")
    print("2. View All Products")
    print("3. Search Products")
    print("4. Update Product")
    print("5. Delete Product")
    print("0. Quit")
    print("================================")


def display_products(products):
    """Print a list of product rows in a readable, labeled format.

    Column order matches the products table:
    id, name, category, price, size, stock.
    """
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
    """Keep asking until the user enters a whole-number size in the allowed range.

    Returns the size as an integer.
    """
    while True:
        entry = input(f"Enter shoe size ({MIN_SIZE}-{MAX_SIZE}): ").strip()
        if entry.isdigit() and MIN_SIZE <= int(entry) <= MAX_SIZE:
            return int(entry)
        print(f"Invalid size. Use a whole number from {MIN_SIZE} to {MAX_SIZE}.")


def main():
    """Run the menu until the user chooses to quit."""
    while True:
        show_menu()

        choice = input("Enter your choice: ").strip()

        # Add a new product
        if choice == "1":
            name = input("Enter product name: ").strip()

            # An empty string would pass NOT NULL, so check for it here
            if not name:
                print("Name cannot be empty.")
                continue

            category = ask_category()
            size = ask_size()

            try:
                price = int(input("Enter price: "))
                stock = int(input("Enter stock quantity: "))

                # Check that price and stock are not negative
                if price < 0 or stock < 0:
                    print("Price and stock cannot be negative.")
                    continue

                add_product(name, category, size, price, stock)
                print("Product added successfully!")

            except ValueError:
                print("Invalid input. Price and stock must be numbers.")
            except sqlite3.IntegrityError:
                # Either a CHECK constraint failed or this name and size already exist
                print("The database rejected this product. It may already exist "
                      "in that size. Use Update Product to change its stock.")

        # View all products
        elif choice == "2":
            print("\nALL PRODUCTS")
            display_products(get_all_products())

        # Search products by category
        elif choice == "3":
            category = ask_category()
            display_products(search_products(category))

        # Update product price and stock
        elif choice == "4":
            try:
                product_id = int(input("Enter product ID: "))
                price = int(input("Enter new price: "))
                stock = int(input("Enter new stock quantity: "))

                if price < 0 or stock < 0:
                    print("Price and stock cannot be negative.")
                    continue

                updated = update_product(product_id, price, stock)

                if updated:
                    print("Product updated successfully!")
                else:
                    print("No product found with that ID.")

            except ValueError:
                print("Invalid input. Please enter numbers only.")
            except sqlite3.IntegrityError:
                print("Price and stock cannot be negative.")

        # Delete a product
        elif choice == "5":
            try:
                product_id = int(input("Enter product ID to delete: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            try:
                deleted = delete_product(product_id)

                if deleted:
                    print("Product deleted successfully!")
                else:
                    print("No product found with that ID.")

            except ValueError as error:
                # Raised by delete_product when the product is part of an order
                print(error)

        # Exit the program
        elif choice == "0":
            print("Thank you for using Frey Kicks Inventory System!")
            break

        else:
            print("Invalid choice. Please select an option from the menu.")


# Only start the menu when this file is run directly
if __name__ == "__main__":
    main()