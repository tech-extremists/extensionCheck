
import datetime  # Used for date and time in sale records
import json  # For saving and loading inventory and sales data to/from JSON files
import os  # For checking file existence when loading data
import logging
from typing import Optional  # For logging operations such as adding items or recording sales

# Configure logging settings to write logs to a file with specific format
logging.basicConfig(filename='store_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Item:
    """Class to represent an item in inventory."""

    def __init__(self, item_id, name, price, quantity=0):
        # Initialize the Item with ID, name, price, quantity, and discount attributes
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.discount = 0  # In percentage, default is 0

    def set_discount(self, discount_percent):
        """Sets a discount on the item if within 0-100%."""
        if 0 <= discount_percent <= 100:
            self.discount = discount_percent
            logging.info(f"Discount set for {self.name}: {self.discount}%")
        else:
            raise ValueError("Discount percent must be between 0 and 100.")

    def get_discounted_price(self):
        """Calculates and returns the price after discount."""
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        """Returns a string representation of the item."""
        return f"{self.name} (ID: {self.item_id}) - ${self.get_discounted_price():.2f} x {self.quantity} units"

    def to_dict(self):
        """Converts item details to a dictionary for easy JSON serialization."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'discount': self.discount
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Item instance from a dictionary (deserialization)."""
        item = cls(data['item_id'], data['name'], data['price'], data['quantity'])
        item.discount = data.get('discount', 0)
        return item


class Inventory:
    """Class to manage the store's inventory."""

    def __init__(self):
        # Initialize inventory with an empty dictionary of items
        self.items = {}

    def add_item(self, item):
        """Adds a new item to inventory if ID is unique."""
        if item.item_id in self.items:
            raise ValueError("Item ID already exists.")
        self.items[item.item_id] = item
        logging.info(f"Added item to inventory: {item}")

    def update_quantity(self, item_id, quantity):
        """Updates quantity of an existing item."""
        if item_id not in self.items:
            raise ValueError("Item ID does not exist.")
        self.items[item_id].quantity = quantity
        logging.info(f"Updated quantity for item {self.items[item_id].name}: {quantity}")

    def apply_discount_to_item(self, item_id, discount_percent):
        """Applies a discount to a single item based on item ID."""
        if item_id not in self.items:
            raise ValueError("Item ID does not exist.")
        self.items[item_id].set_discount(discount_percent)

    def apply_discount_to_all(self, discount_percent):
        """Applies a discount to all items in inventory."""
        for item in self.items.values():
            item.set_discount(discount_percent)
        logging.info(f"Applied {discount_percent}% discount to all items")

    def adjust_quantity(self, item_id, quantity_change):
        """Adjusts quantity for a specific item by a given amount (positive or negative)."""
        if item_id not in self.items:
            raise ValueError("Item ID does not exist.")
        item = self.items[item_id]
        if item.quantity + quantity_change < 0:
            raise ValueError("Insufficient quantity in stock.")
        item.quantity += quantity_change
        logging.info(f"Adjusted quantity for {item.name}: {item.quantity} units remaining")

    def find_item(self, item_id):
        """Finds an item by its ID, returns None if not found."""
        return self.items.get(item_id, None)

    def generate_report(self):
        """Prints a report of all items in inventory."""
        print("\n--- Inventory Report ---")
        for item in self.items.values():
            print(item)

    def search_items(self, name_keyword):
        """Searches for items by name keyword, printing results."""
        results = [item for item in self.items.values() if name_keyword.lower() in item.name.lower()]
        print(f"\n--- Search Results for '{name_keyword}' ---")
        for item in results:
            print(item)

    def save_inventory(self, filename='inventory.json'):
        """Saves inventory to a JSON file."""
        with open(filename, 'w') as file:
            json.dump([item.to_dict() for item in self.items.values()], file)

    def load_inventory(self, filename='inventory.json'):
        """Loads inventory from a JSON file if it exists."""
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                items_data = json.load(file)
                self.items = {item_data['item_id']: Item.from_dict(item_data) for item_data in items_data}
            logging.info("Loaded inventory from file.")
        else:
            print("No inventory file found.")
            logging.warning("Attempted to load non-existing inventory file.")


class User:
    """Class representing a user of the system."""
    
    def __init__(self, username, role='customer'):
        self.username = username
        self.role = role.lower()  # Role of user, either 'admin' or 'customer'
        if self.role not in ['admin', 'customer']:
            raise ValueError("Role must be 'admin' or 'customer'.")

    def is_admin(self):
        """Checks if user has admin privileges."""
        return self.role == 'admin'

    def __str__(self):
        """Returns a string representation of the user."""
        return f"Username: {self.username}, Role: {self.role.capitalize()}"


class Sale:
    """Class to represent a completed sale."""

    def __init__(self, items, total_cost, customer_name):
        self.items = items  # List of items sold
        self.total_cost = total_cost  # Total cost of the sale
        self.date = datetime.datetime.now()  # Timestamp of sale
        self.customer_name = customer_name  # Name of the customer

    def __str__(self):
        """Returns a string summary of the sale."""
        items_str = ", ".join([f"{item['name']} x {item['quantity']}" for item in self.items])
        return f"Date: {self.date} | Customer: {self.customer_name} | Items: {items_str} | Total: ${self.total_cost:.2f}"

    def to_dict(self):
        """Converts sale details to a dictionary for JSON serialization."""
        return {
            'date': self.date.isoformat(),
            'customer_name': self.customer_name,
            'items': self.items,
            'total_cost': self.total_cost
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Sale instance from a dictionary (deserialization)."""
        sale = cls(data['items'], data['total_cost'], data['customer_name'])
        sale.date = datetime.datetime.fromisoformat(data['date'])
        return sale


class SalesHistory:
    """Class to manage sales history."""

    def __init__(self):
        # Initialize with an empty list to store Sale instances
        self.sales = []

    def record_sale(self, sale):
        """Records a sale by adding it to sales history."""
        self.sales.append(sale)
        logging.info(f"Recorded sale: {sale}")

    def generate_sales_report(self):
        """Generates and prints a report of all sales."""
        print("\n--- Sales Report ---")
        for sale in self.sales:
            print(sale)
        print("Total Revenue:", self.get_total_revenue())

    def get_total_revenue(self):
        """Calculates total revenue from all recorded sales."""
        return sum(sale.total_cost for sale in self.sales)

    def get_sales_by_date(self, date):
        """Retrieves all sales that occurred on a specific date."""
        date_sales = [sale for sale in self.sales if sale.date.date() == date]
        return date_sales

    def save_sales_history(self, filename='sales_history.json'):
        """Saves sales history to a JSON file."""
        with open(filename, 'w') as file:
            json.dump([sale.to_dict() for sale in self.sales], file)
        logging.info("Saved sales history to file.")

    def load_sales_history(self, filename='sales_history.json'):
        """Loads sales history from a JSON file if it exists."""
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                sales_data = json.load(file)
                self.sales = [Sale.from_dict(sale_data) for sale_data in sales_data]
            logging.info("Loaded sales history from file.")
        else:
            print("No sales history file found.")
            logging.warning("Attempted to load non-existing sales history file.")


class Store:
    """Main class to manage the store operations."""

    def __init__(self, user):
        # Initialize store with inventory, sales history, and user instance
        self.inventory = Inventory()
        self.sales_history = SalesHistory()
        self.user = user

    def add_item_to_inventory(self, item_id, name, price, quantity):
        """Adds a new item to inventory (admin-only)."""
        if not self.user.is_admin():
            raise PermissionError("Only admins can add items to the inventory.")
        item = Item(item_id, name, price, quantity)
        self.inventory.add_item(item)

    def update_inventory_quantity(self, item_id, quantity):
        """Updates item quantity in inventory (admin-only)."""
        if not self.user.is_admin():
            raise PermissionError("Only admins can update item quantity.")
        self.inventory.update_quantity(item_id, quantity)

    def apply_discount(self, item_id=None, discount_percent=0):
        """Applies discount to a specific item or all items (admin-only)."""
        if not self.user.is_admin():
            raise PermissionError("Only admins can apply discounts.")
        if item_id:
            self.inventory.apply_discount_to_item(item_id, discount_percent)
        else:
            self.inventory.apply_discount_to_all(discount_percent)

    def checkout_cart(self, cart, customer_name):
        """Processes checkout by calculating total cost and recording the sale."""
        total_cost = cart.checkout()
        items = [{"name": item.item.name, "quantity": item.quantity} for item in cart.cart_items]
        sale = Sale(items, total_cost, customer_name)
        self.sales_history.record_sale(sale)
        logging.info(f"Checkout completed for {customer_name}: Total cost ${total_cost:.2f}")
        return total_cost

    def show_inventory(self):
        """Displays all items in the inventory."""
        self.inventory.generate_report()

    def search_inventory(self, name_keyword):
        """Searches for items in inventory based on a name keyword."""
        self.inventory.search_items(name_keyword)

    def show_sales_history(self):
        """Displays all recorded sales in sales history."""
        self.sales_history.generate_sales_report()

    def save_data(self):
        """Saves both inventory and sales history data to files."""
        self.inventory.save_inventory()
        self.sales_history.save_sales_history()

    def load_data(self):
        """Loads both inventory and sales history data from files."""
        self.inventory.load_inventory()
        self.sales_history.load_sales_history()


def main():
    """Main function to run the store application."""

    # Collects user information for accessing the store system
    username = input("Enter your username: ")
    role = input("Enter your role (admin/customer): ").strip()
    user = User(username, role)  # Creates a User instance
    store = Store(user)  # Creates a Store instance

    # Load previous data if available
    store.load_data()
    cart = ShoppingCart()  # Initialize shopping cart for this session

    while True:
        # Display options for the user in the store management system
        print("\n--- Store Management System ---")
        print("1. Add Item to Inventory")
        print("2. Update Inventory Quantity")
        print("3. View Inventory")
        print("4. Search Inventory")
        print("5. Add Discount to Item")
        print("6. Apply Discount to All Items")
        print("7. View Sales History")
        print("8. Save Data")
        print("9. Load Data")
        print("10. Exit")

        # Prompt user to choose an option
        choice = input("Enter your choice (1-10): ")

        try:
            if choice == '1':
                item_id = int(input("Enter item ID: "))
                name = input("Enter item name: ")
                price = float(input("Enter item price: "))
                quantity = int(input("Enter item quantity: "))
                store.add_item_to_inventory(item_id, name, price, quantity)
                print("Item added to inventory.")

            elif choice == '2':
                item_id = int(input("Enter item ID: "))
                quantity = int(input("Enter new quantity: "))
                store.update_inventory_quantity(item_id, quantity)
                print("Inventory quantity updated.")

            elif choice == '3':
                store.show_inventory()

            elif choice == '4':
                keyword = input("Enter name keyword to search: ")
                store.search_inventory(keyword)

            elif choice == '5':
                item_id = int(input("Enter item ID to discount: "))
                discount = float(input("Enter discount percent (0-100): "))
                store.apply_discount(item_id, discount)
                print("Discount applied to item.")

            elif choice == '6':
                discount = float(input("Enter discount percent for all items (0-100): "))
                store.apply_discount(discount_percent=discount)
                print("Discount applied to all items.")

            elif choice == '7':
                store.show_sales_history()

            elif choice == '8':
                store.save_data()
                print("Data saved.")

            elif choice == '9':
                store.load_data()
                print("Data loaded.")

            elif choice == '10':
                print("Exiting program.")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 10.")

        except (ValueError, PermissionError) as e:
            print(f"Error: {e}")
            
def _temporal_split_from_datetime(
    example_datetime: datetime.datetime
) -> Optional[str]:
    """Finds the split name using the example datetime."""
    end_train_datetime = datetime.datetime.strptime('2022-01-01', '%Y-%m-%d')
    end_valid_datetime = datetime.datetime.strptime('2022-05-01', '%Y-%m-%d')
    end_test_datetime = datetime.datetime.strptime('2022-06-01', '%Y-%m-%d')

    if example_datetime < end_train_datetime:
        return 'train'
    elif example_datetime < end_valid_datetime:
        return 'validation'
    elif example_datetime < end_test_datetime:
        return 'test'
    else:
        return None
    
    
if __name__ == "__main__":
    main()