# shopping_cart_manager.py

def shopping_cart_manager():
    cart = []
    while True:
        print("\nShopping Cart Manager")
        print("1. Add item")
        print("2. Remove a specific item")
        print("3. Remove the last added item")
        print("4. Display items in alphabetical order")
        print("5. Display cart contents with indices")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            item = input("Enter item to add: ")
            cart.append(item)
            print(f"Added '{item}' to cart.")
        elif choice == "2":
            item = input("Enter item to remove: ")
            if item in cart:
                cart.remove(item)
                print(f"Removed '{item}' from cart.")
            else:
                print(f"'{item}' not found in cart.")
        elif choice == "3":
            if cart:
                removed = cart.pop()
                print(f"Removed last item: '{removed}'")
            else:
                print("Cart is empty.")
        elif choice == "4":
            if cart:
                print("Items in alphabetical order:")
                for item in sorted(cart):
                    print(item)
            else:
                print("Cart is empty.")
        elif choice == "5":
            if cart:
                print("Cart contents with indices:")
                for i, item in enumerate(cart):
                    print(f"{i}: {item}")
            else:
                print("Cart is empty.")
        elif choice == "6":
            print("Exiting Shopping Cart Manager.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    shopping_cart_manager()
