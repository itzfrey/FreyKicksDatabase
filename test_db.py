
from db import (
    add_product,
    get_all_products,
    search_products,
    update_product,
    delete_product
)

# Test 1: Add sample sneakers
print("ADDING PRODUCTS...")

id1 = add_product("Air Force 1", "Sneakers", "42", 45000, 5)
id2 = add_product("Puma Speedcat", "Sneakers", "43", 55000, 3)
id3 = add_product("Timberland Boots", "Boots", "44", 85000, 4)
id4 = add_product("Adidas Samba", "Sneakers", "42", 60000, 6)
id5 = add_product("Nike Slides", "Slides", "42", 20000, 8)

print("Products added successfully!\n")


# Test 2: Display all products
print("ALL PRODUCTS:")

for product in get_all_products():
    print(product)


# Test 3: Search by category
print("\nSEARCHING FOR SNEAKERS:")

results = search_products("Sneakers")

for product in results:
    print(product)


# Test 4: Update a product
print("\nUPDATING AIR FORCE 1:")

updated = update_product(id1, 50000, 10)

if updated:
    print("Product updated successfully!")
else:
    print("Product not found.")


# Test 5: Delete a product
print("\nDELETING PUMA SPEEDCAT:")

deleted = delete_product(id2)

if deleted:
    print("Product deleted successfully!")
else:
    print("Product not found.")


# Test 6: Try deleting an ID that doesn't exist
print("\nTESTING INVALID PRODUCT ID:")

deleted = delete_product(99999)

if deleted:
    print("Product deleted successfully!")
else:
    print("No product found with that ID.")


# Test 7: Display products after modifications
print("\nFINAL PRODUCT LIST:")

for product in get_all_products():
    print(product)
