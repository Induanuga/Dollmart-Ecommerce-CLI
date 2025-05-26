import hashlib
import sqlite3
import random
from datetime import datetime

def create_database():
    """Create database and required tables if they don't exist"""
    conn = sqlite3.connect('dollmart.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        customer_type TEXT,
        visit_count INTEGER DEFAULT 0
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        username TEXT,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (username) REFERENCES users (username),
        FOREIGN KEY (product_id) REFERENCES products (id),
        PRIMARY KEY (username, product_id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        total_amount REAL,
        order_date TEXT,
        otp TEXT,
        status TEXT DEFAULT 'placed',
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    cursor.execute("SELECT * FROM users WHERE username = 'mngr'")
    if cursor.fetchone() is None:
        hashed_password = hashlib.sha256("123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role, visit_count) VALUES (?, ?, ?, NULL)", 
                    ('mngr', hashed_password, 'manager'))
    conn.commit()
    conn.close()


class User:
    def __init__(self, username, role, customer_type=None, visit_count=0):
        self.username = username
        self.role = role
        self.customer_type = customer_type
        self.visit_count = visit_count

    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register():
        """Register a new customer"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        while True:
            username = input("Enter username: ")
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                print("Username already exists. Please choose another.")
            else:
                break
        while True:
            password = input("Enter password (minimum 3 characters): ")
            if len(password) >= 3:
                break
            print("Password must be at least 3 characters long.")
        hashed_password = User.hash_password(password)
        while True:
            print("Select customer type:")
            print("1. Individual")
            print("2. Retail Store")
            choice = input("Enter your choice (1-2): ")
            if choice == '1':
                customer_type = 'individual'
                break
            elif choice == '2':
                customer_type = 'retail'
                break
            else:
                print("Invalid choice. Please try again.")
        cursor.execute(
            "INSERT INTO users (username, password, role, customer_type, visit_count) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, 'customer', customer_type, 0)
        )
        conn.commit()
        conn.close()
        print(f"Registration successful! Welcome, {username}!")
    
    @staticmethod
    def login():
        """Login a user and return User object if successful"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        username = input("Enter username: ")
        password = input("Enter password: ")
        hashed_password = User.hash_password(password)
        cursor.execute("SELECT username, role, customer_type, visit_count FROM users WHERE username = ? AND password = ?", 
                     (username, hashed_password))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        else:
            print("Invalid username or password.")
            return None


class Product:
    def __init__(self, id, name, price, category, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.quantity = quantity
    
    @staticmethod
    def add_product():
        """Add a new product to the database"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        name = input("Enter product name: ")
        while True:
            try:
                price = float(input("Enter product price: "))
                if price <= 0:
                    raise ValueError("Price must be positive.")
                break
            except ValueError as e:
                print(e)
        category = input("Enter product category: ")
        while True:
            try:
                quantity = int(input("Enter product quantity: "))
                if quantity <= 0:
                    raise ValueError("Quantity must be positive.")
                break
            except ValueError as e:
                print(e)
        cursor.execute(
            "INSERT INTO products (name, price, category, quantity) VALUES (?, ?, ?, ?)",
            (name, price, category, quantity)
        )
        conn.commit()
        conn.close()
        print(f"Product '{name}' added successfully!")
    
    @staticmethod
    def remove_product():
        """Remove a product from the database"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            print("No products available in the store.")
            conn.close()
            return
        Product.view_all_products()
        while True:
            try:
                product_id = int(input("Enter product ID to remove: "))
                cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
                if not cursor.fetchone():
                    print("Product ID does not exist.")
                    continue
                break
            except ValueError:
                print("Please enter a valid product ID.")
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
        conn.commit()
        conn.close()
        print(f"Product with ID {product_id} removed successfully!")
    

    @staticmethod
    def update_product():
        """Update product details"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            print("No products available in the store.")
            conn.close()
            return
        Product.view_all_products()
        while True:
            try:
                product_id = int(input("Enter product ID to update: "))
                cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
                if not cursor.fetchone():
                    print("Product ID does not exist.")
                    continue
                break
            except ValueError:
                print("Please enter a valid product ID.")
        print("What would you like to update?")
        print("1. Name")
        print("2. Price")
        print("3. Category")
        print("4. Quantity")
        while True:
            choice = input("Enter your choice (1-4): ")
            if choice == '1':
                new_value = input("Enter new name: ")
                cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_value, product_id))
                break
            elif choice == '2':
                try:
                    new_value = float(input("Enter new price: "))
                    if new_value <= 0:
                        print("Price must be positive.")
                        continue
                    cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_value, product_id))
                    break
                except ValueError:
                    print("Please enter a valid price.")
            elif choice == '3':
                new_value = input("Enter new category: ")
                cursor.execute("UPDATE products SET category = ? WHERE id = ?", (new_value, product_id))
                break
            elif choice == '4':
                try:
                    new_value = int(input("Enter new quantity: "))
                    if new_value < 0:
                        print("Quantity cannot be negative.")
                        continue
                    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_value, product_id))
                    break
                except ValueError:
                    print("Please enter a valid quantity.")
            else:
                print("Invalid choice. Please try again.")
        conn.commit()
        conn.close()
        print("Product updated successfully!")
    
    @staticmethod
    def view_all_products():
        """View all products in the database"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            print("No products available in the store.")
            conn.close()
            return
        cursor.execute("SELECT id, name, price, category, quantity FROM products")
        products = cursor.fetchall()
        conn.close()
        available_quantities = Cart.update_product_availability()
        print("\n=== Products List ===")
        print("ID | Name | Price | Category | Total Quantity | Available Quantity")
        print("-" * 80)
        for product in products:
            product_id = product[0]
            available = available_quantities.get(product_id, 0)
            print(f"{product[0]} | {product[1]} | ${product[2]:.2f} | {product[3]} | {product[4]} | {available}")
        print("-" * 80)    

    @staticmethod
    def search_products():
        """Search products by category or name"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            print("No products available in the store.")
            conn.close()
            return
        print("Search by:")
        print("1. Category")
        print("2. Name")
        print("3. Keyword (matches both name and category)")
        while True:
            choice = input("Enter your choice (1-3): ")
            if choice == '1':
                search_term = input("Enter category to search: ")
                cursor.execute("SELECT id, name, price, category, quantity FROM products WHERE category LIKE ?", 
                            (f'%{search_term}%',))
                break
            elif choice == '2':
                search_term = input("Enter name to search: ")
                cursor.execute("SELECT id, name, price, category, quantity FROM products WHERE name LIKE ?", 
                            (f'%{search_term}%',))
                break
            elif choice == '3':
                search_term = input("Enter keyword to search: ")
                cursor.execute("SELECT id, name, price, category, quantity FROM products WHERE name LIKE ? OR category LIKE ?", 
                            (f'%{search_term}%', f'%{search_term}%'))
                break
            else:
                print("Invalid choice. Please try again.")
        products = cursor.fetchall()
        conn.close()
        if not products:
            print("No matching products found.")
            return
        print("\n=== Search Results ===")
        print("ID | Name | Price | Category | Quantity")
        print("-" * 60)
        for product in products:
            print(f"{product[0]} | {product[1]} | ${product[2]:.2f} | {product[3]} | {product[4]}")
        print("-" * 60)


class Cart:
    @staticmethod
    def add_to_cart(username):
        """Add item to user's cart"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            print("No products available in the store to add to cart.")
            conn.close()
            return
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity > 0")
        in_stock_count = cursor.fetchone()[0]
        if in_stock_count == 0:
            print("Sorry, all products are currently out of stock.")
            conn.close()
            return
        Product.view_all_products()
        while True:
            try:
                product_id = int(input("Enter product ID to add to cart: "))
                cursor.execute("SELECT id, quantity FROM products WHERE id = ?", (product_id,))
                product = cursor.fetchone()
                if not product:
                    raise ValueError("Product ID does not exist.")
                if product[1] <= 0:
                    print("Product is out of stock.")
                    continue
                break
            except ValueError as e:
                print(e)
        cursor.execute("SELECT quantity FROM cart WHERE username = ? AND product_id = ?", 
                     (username, product_id))
        cart_item = cursor.fetchone()
        if cart_item:
            while True:
                try:
                    add_quantity = int(input(f"Product already in cart (quantity: {cart_item[0]}). How many more to add? "))
                    if add_quantity <= 0:
                        print("Quantity must be positive.")
                        continue
                    if add_quantity + cart_item[0] > product[1]:
                        print(f"Not enough stock. Available: {product[1]}")
                        if product[1] <= cart_item[0]:
                            print("You already have all available stock in your cart.")
                            break
                        continue
                    cursor.execute("UPDATE cart SET quantity = quantity + ? WHERE username = ? AND product_id = ?", 
                                (add_quantity, username, product_id))
                    break
                except ValueError:
                    print("Please enter a valid quantity.")
        else:
            while True:
                try:
                    quantity = int(input("Enter quantity: "))
                    if quantity <= 0:
                        print("Quantity must be positive.")
                        continue
                    if quantity > product[1]:
                        print(f"Not enough stock. Available: {product[1]}")
                        continue
                    cursor.execute("INSERT INTO cart (username, product_id, quantity) VALUES (?, ?, ?)", 
                                 (username, product_id, quantity))
                    break
                except ValueError:
                    print("Please enter a valid quantity.")
        conn.commit()
        conn.close()
        print("Item added to cart successfully!")
    
    @staticmethod
    def remove_from_cart(username):
        """Remove item from user's cart"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        Cart.view_cart(username)
        cursor.execute("""
            SELECT c.product_id, p.name, c.quantity 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.username = ?
        """, (username,))
        cart_items = cursor.fetchall()
        if not cart_items:
            conn.close()
            return
        while True:
            try:
                product_id = int(input("Enter product ID to remove from cart: "))
                cursor.execute("SELECT product_id FROM cart WHERE username = ? AND product_id = ?", 
                             (username, product_id))
                if not cursor.fetchone():
                    print("Product not in cart.")
                    continue
                break
            except ValueError:
                print("Please enter a valid product ID.")
        print("1. Remove completely")
        print("2. Reduce quantity")
        while True:
            choice = input("Enter your choice (1-2): ")
            if choice == '1':
                cursor.execute("DELETE FROM cart WHERE username = ? AND product_id = ?", 
                             (username, product_id))
                break
            elif choice == '2':
                cursor.execute("SELECT quantity FROM cart WHERE username = ? AND product_id = ?", 
                             (username, product_id))
                current_quantity = cursor.fetchone()[0]
                while True:
                    try:
                        reduce_by = int(input(f"Current quantity: {current_quantity}. Reduce by how many? "))
                        if reduce_by <= 0:
                            print("Quantity must be positive.")
                            continue
                        if reduce_by >= current_quantity:
                            print("This will remove the item completely.")
                            cursor.execute("DELETE FROM cart WHERE username = ? AND product_id = ?", 
                                         (username, product_id))
                        else:
                            cursor.execute("UPDATE cart SET quantity = quantity - ? WHERE username = ? AND product_id = ?", 
                                         (reduce_by, username, product_id))
                        break
                    except ValueError:
                        print("Please enter a valid quantity.")
                break
            else:
                print("Invalid choice. Please try again.")
        conn.commit()
        conn.close()
        print("Cart updated successfully!")
    
    @staticmethod
    def view_cart(username):
        """View user's cart"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT customer_type FROM users WHERE username = ?", (username,))
        customer_type = cursor.fetchone()[0]
        cursor.execute("""
            SELECT c.product_id, p.name, p.price, c.quantity, p.category
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.username = ?
        """, (username,))
        cart_items = cursor.fetchall()
        conn.close()
        if not cart_items:
            print("Your cart is empty.")
            return
        print("\n=== Your Cart ===")
        print("ID | Name | Price | Quantity | Subtotal")
        print("-" * 60)
        total = 0
        for item in cart_items:
            product_id, name, price, quantity, category = item
            if customer_type == 'retail':
                discount_price = price * 0.9  # 10% discount for retail
                subtotal = discount_price * quantity
                print(f"{product_id} | {name} | ${price:.2f} (${discount_price:.2f} with retail discount) | {quantity} | ${subtotal:.2f}")
            else:
                subtotal = price * quantity
                print(f"{product_id} | {name} | ${price:.2f} | {quantity} | ${subtotal:.2f}")
            total += subtotal
        print("-" * 60)
        print(f"Total: ${total:.2f}")
        return total
    
    @staticmethod
    def place_order(username):
        """Place an order with items in cart"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cart WHERE username = ?", (username,))
        if cursor.fetchone()[0] == 0:
            print("Your cart is empty.")
            conn.close()
            return
        cursor.execute("SELECT customer_type, visit_count FROM users WHERE username = ?", (username,))
        customer_data = cursor.fetchone()
        customer_type = customer_data[0]
        visit_count = customer_data[1]
        total = Cart.view_cart(username)
        discount_applied = False
        if (visit_count + 1) % 3 == 0:
            print("\n🎉 Congratulations! You are eligible for a 10% discount on this order!")
            discount_applied = True
            total = total * 0.9
            print(f"Discounted Total: ${total:.2f}")
        while True:
            confirm = input(f"\nTotal amount to pay: ${total:.2f}\nConfirm order? (y/n): ").lower()
            if confirm in ['y', 'n']:
                break
            print("Please enter 'y' or 'n'.")
        if confirm == 'n':
            print("Order cancelled.")
            conn.close()
            return
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO orders (username, total_amount, order_date, otp, status) VALUES (?, ?, ?, ?, ?)",
            (username, total, order_date, otp, "placed")
        )
        order_id = cursor.lastrowid
        cursor.execute("""
            SELECT c.product_id, p.price, c.quantity 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.username = ?
        """, (username,))
        cart_items = cursor.fetchall()
        for item in cart_items:
            product_id, price, quantity = item
            if customer_type == 'retail':
                price = price * 0.9
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, price)
            )
            cursor.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                (quantity, product_id)
            )
        cursor.execute(
            "UPDATE users SET visit_count = visit_count + 1 WHERE username = ?",
            (username,)
        )
        cursor.execute("DELETE FROM cart WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        
        print("\n==== Order Placed Successfully! ====")
        print(f"Order ID: {order_id}")
        print(f"Order Date: {order_date}")
        print(f"Total Amount: ${total:.2f}")
        print(f"Your OTP for order confirmation: {otp}")
        print("IMPORTANT: Please keep this OTP. The manager will use it to confirm your order delivery.")
        if discount_applied:
            print("10% Loyalty Discount Applied!")
        print("Thank you for shopping with Dollmart!")

    @staticmethod
    def update_product_availability():
        """Update product availability by considering items in carts"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, quantity FROM products")
        products = {product[0]: product[1] for product in cursor.fetchall()}
        cursor.execute("""
            SELECT product_id, SUM(quantity) as reserved
            FROM cart
            GROUP BY product_id
        """)
        reserved_items = cursor.fetchall()
        available_quantities = products.copy()
        for product_id, reserved in reserved_items:
            if product_id in available_quantities:
                available_quantities[product_id] -= reserved
        conn.close()
        return available_quantities


class Order:
    @staticmethod
    def view_order_history(username):
        """View order history for a user"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, total_amount, order_date, status FROM orders WHERE username = ? ORDER BY order_date DESC",
            (username,)
        )
        orders = cursor.fetchall()
        if not orders:
            print("You have no previous orders.")
            conn.close()
            return
        print("\n=== Your Order History ===")
        for order in orders:
            order_id, total_amount, order_date, status = order
            print(f"\nOrder ID: {order_id}")
            print(f"Date: {order_date}")
            print(f"Status: {status.upper()}")
            print(f"Total Amount: ${total_amount:.2f}")
            cursor.execute("""
                SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as subtotal 
                FROM order_items oi 
                JOIN products p ON oi.product_id = p.id 
                WHERE oi.order_id = ?
            """, (order_id,))
            items = cursor.fetchall()
            print("Items:")
            print("Name | Quantity | Price | Subtotal")
            print("-" * 60)
            for item in items:
                name, quantity, price, subtotal = item
                print(f"{name} | {quantity} | ${price:.2f} | ${subtotal:.2f}")
            print("-" * 60)
        conn.close()
    
    @staticmethod
    def view_all_orders():
        """View all orders (manager only)"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.id, o.username, o.total_amount, o.order_date, 
                   COUNT(oi.product_id) as items_count, 
                   u.customer_type, o.status
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN users u ON o.username = u.username
            GROUP BY o.id
            ORDER BY o.order_date DESC
            """
        )
        orders = cursor.fetchall()
        if not orders:
            print("No orders found.")
            conn.close()
            return
        print("\n=== All Orders ===")
        print("ID | Username | Customer Type | Items | Total | Date | Status")
        print("-" * 90)
        for order in orders:
            order_id, username, total, date, items_count, customer_type, status = order
            print(f"{order_id} | {username} | {customer_type} | {items_count} | ${total:.2f} | {date} | {status.upper()}")
        print("-" * 90)
        while True:
            view_detail = input("View order details? (y/n): ").lower()
            if view_detail == 'y':
                try:
                    order_id = int(input("Enter Order ID: "))
                    cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
                    if not cursor.fetchone():
                        print("Order ID does not exist.")
                        continue
                    cursor.execute(
                        "SELECT username, total_amount, order_date, status FROM orders WHERE id = ?",
                        (order_id,)
                    )
                    order_details = cursor.fetchone()
                    username, total, date, status = order_details
                    print(f"\nOrder ID: {order_id}")
                    print(f"Customer: {username}")
                    print(f"Date: {date}")
                    print(f"Status: {status.upper()}")
                    print(f"Total: ${total:.2f}")
                    cursor.execute("""
                        SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as subtotal 
                        FROM order_items oi 
                        JOIN products p ON oi.product_id = p.id 
                        WHERE oi.order_id = ?
                    """, (order_id,))
                    items = cursor.fetchall()
                    print("Items:")
                    print("Name | Quantity | Price | Subtotal")
                    print("-" * 60)
                    for item in items:
                        name, quantity, price, subtotal = item
                        print(f"{name} | {quantity} | ${price:.2f} | ${subtotal:.2f}")
                    print("-" * 60)
                except ValueError:
                    print("Please enter a valid Order ID.")
            elif view_detail == 'n':
                break
            else:
                print("Please enter 'y' or 'n'.")
        conn.close()
    
    @staticmethod
    def confirm_order():
        """Confirm order delivery by verifying OTP"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, order_date, total_amount
            FROM orders 
            WHERE status = 'placed'
            ORDER BY order_date ASC
            """
        )
        pending_orders = cursor.fetchall()
        if not pending_orders:
            print("No pending orders to confirm.")
            conn.close()
            return
            
        print("\n=== Pending Orders ===")
        print("ID | Username | Date | Total Amount")
        print("-" * 60)
        for order in pending_orders:
            order_id, username, date, total = order
            print(f"{order_id} | {username} | {date} | ${total:.2f}")
        print("-" * 60)
        
        while True:
            try:
                order_id = int(input("Enter Order ID to confirm delivery: "))
                cursor.execute("SELECT id, otp FROM orders WHERE id = ? AND status = 'placed'", (order_id,))
                order_data = cursor.fetchone()
                if not order_data:
                    print("Invalid Order ID or order is already delivered.")
                    continue
                break
            except ValueError:
                print("Please enter a valid Order ID.")
                
        otp = input("Enter OTP provided by the customer: ")
        
        if otp == order_data[1]:
            cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = ?", (order_id,))
            conn.commit()
            print(f"Order #{order_id} has been confirmed as delivered!")
        else:
            print("Invalid OTP. Order status not updated.")
            
        conn.close()
    
    @staticmethod
    def view_all_customers():
        """View all customers (manager only)"""
        conn = sqlite3.connect('dollmart.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT username, customer_type, visit_count, 
                   (SELECT COUNT(*) FROM orders WHERE orders.username = users.username) as orders_count
            FROM users
            WHERE role = 'customer'
            ORDER BY orders_count DESC
            """
        )
        customers = cursor.fetchall()
        if not customers:
            print("No customers found.")
            conn.close()
            return
        print("\n=== All Customers ===")
        print("Username | Type | Visit Count | Orders Count")
        print("-" * 60)
        for customer in customers:
            username, customer_type, visit_count, orders_count = customer
            print(f"{username} | {customer_type} | {visit_count} | {orders_count}")
        print("-" * 60)
        conn.close()


def manager_menu():
    """Display manager menu and handle options"""
    while True:
        print("\n=== Manager Menu ===")
        print("1. Add Product")
        print("2. Remove Product")
        print("3. Update Product Details")
        print("4. View All Products")
        print("5. View All Customers")
        print("6. View All Orders")
        print("7. Confirm Order Delivery")
        print("8. Logout")
        choice = input("Enter your choice (1-8): ")
        if choice == '1':
            Product.add_product()
        elif choice == '2':
            Product.remove_product()
        elif choice == '3':
            Product.update_product()
        elif choice == '4':
            Product.view_all_products()
        elif choice == '5':
            Order.view_all_customers()
        elif choice == '6':
            Order.view_all_orders()
        elif choice == '7':
            Order.confirm_order()
        elif choice == '8':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def customer_menu(user):
    """Display customer menu and handle options"""
    while True:
        print(f"\n=== Customer Menu ({user.username}) ===")
        print("1. View All Products")
        print("2. Search Products")
        print("3. Add Item to Cart")
        print("4. Remove Item from Cart")
        print("5. View Cart")
        print("6. Place Order")
        print("7. View Order History")
        print("8. Logout")
        choice = input("Enter your choice (1-8): ")
        if choice == '1':
            Product.view_all_products()
        elif choice == '2':
            Product.search_products()
        elif choice == '3':
            Cart.add_to_cart(user.username)
        elif choice == '4':
            Cart.remove_from_cart(user.username)
        elif choice == '5':
            Cart.view_cart(user.username)
        elif choice == '6':
            Cart.place_order(user.username)
        elif choice == '7':
            Order.view_order_history(user.username)
        elif choice == '8':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    """Main function to run the Dollmart e-commerce system"""
    create_database()
    while True:
        print("\n=== Welcome to Dollmart E-Commerce System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        if choice == '1':
            User.register()
        elif choice == '2':
            user = User.login()
            if user:
                if user.role == 'manager':
                    manager_menu()
                else:
                    customer_menu(user)
        elif choice == '3':
            print("Thank you for using Dollmart E-Commerce System.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()