# Dollmart E-Commerce System

A command-line e-commerce system for managing users, products, carts, and orders, with manager and customer roles, discounts, and secure authentication.

---

## How to Run

- **To run the app:**
  ```
  cd src
  python3 dollmart.py
  ```
- **To run test cases:**
  ```
  cd testcases
  pytest test_dollmart.py
  ```

---


## Features

- User registration and login (with SHA-256 password hashing)
- Manager and customer roles
- Product inventory management (total and available quantities)
- Cart system with reservation logic
- Order placement, history, and OTP-based delivery confirmation
- Discounts for retail and loyal customers
- Persistent storage with SQLite
- Comprehensive test suite with pytest

---


## Assumptions
### 1. Cart System
- When a user adds items to their cart, those items are considered **"reserved"** and reduce the available quantity shown to all users.  
  - **Example:** If `ItemA` has **Total Quantity (TQ) = 10** and **Available Quantity (AQ) = 10**, and `UserA` adds 3 to their cart:  
    - All users will now see **TQ = 10, AQ = 7**.  
  - If `UserA` places an order with **3 of ItemA**, the new values will be:  
    - **TQ = 7, AQ = 7**.  

- **Users cannot add more items to their cart than are available in stock.**  
- Users can **remove items** from the cart completely or **reduce the quantity**.  
  - If a user reduces the cart quantity **greater than or equal to the current amount**, the item is **removed completely**.  
- **Items in a cart are reserved but not removed from inventory** until the order is placed.  



### 2. Product Inventory Management
- **Total Quantity (TQ):** The absolute quantity of a product in the store inventory.  
- **Available Quantity (AQ):** `TQ - Items in users' carts`.  

- When a user **adds items** to their cart:  
  - `AQ` decreases immediately, but `TQ` remains unchanged.  

- When an order is **placed**:  
  - `TQ` decreases permanently.  

- When viewing products, both **Total Quantity (TQ) and Available Quantity (AQ)** are displayed to reflect:  
  - What is in stock.  
  - What is available for new orders.  

- **Manager updates to product quantities** modify both **TQ and AQ** accordingly.  



### 3. Customer Types and Discounts
- **Retail Customers:** Automatically receive a **10% discount** on all purchases.  
- **Regular Customers:** Receive a **loyalty discount of 10%** on their entire order on every **third visit**.  
  - **(i.e., visit_count = 3, 6, 9, etc.)**  
  - The visit count **only increases with each successful order**, not each login.  



### 4. Order Management
- Each order is assigned a **unique Order ID** and a **One-Time Password (OTP)**.  
- **The OTP is required** for order confirmation by the **manager during delivery**.  
- Orders have **status tracking**:  
  - `"Placed"` → `"Delivered"`.  
- **Order history is maintained** for all users.  



### 5. Security and Authentication
- **Passwords are stored using SHA-256 hashing** for enhanced security.  
- **Manager accounts have special privileges** for:  
  - Inventory Management  
  - Order Management  
- A **default manager account** is created on first run:  
  - **Username:** `mngr`  
  - **Password:** `123`  

---


## Design Rationale

### **Class Division** :

#### **User Class**
- **Reason:** Separates authentication and user management from other functionality.  
- **Benefit:** Easier to maintain user-related features and security in one place.  

#### **Product Class**
- **Reason:** Isolates inventory management operations.  
- **Benefit:** Centralizes product-related code for better organization.  

#### **Cart Class**
- **Reason:** Encapsulates shopping cart functionality.  
- **Benefit:** Keeps temporary user selections separate from permanent inventory.  

#### **Order Class**
- **Reason:** Handles completed transactions.  
- **Benefit:** Maintains clean separation between active shopping and order history/processing.  


### **Technology Choices** :

#### **SQLite Database**
- **Reason:** Lightweight, serverless database requiring no configuration.  
- **Benefit:** Self-contained in a single file, perfect for smaller applications with moderate traffic.  
- **Alternative Considered:** MySQL was considered but deemed overkill for this application.  

#### **Python Standard Library**
- **Reason:** Built-in modules (`sqlite3`, `hashlib`, `datetime`) minimize dependencies.  
- **Benefit:** Simplifies deployment with no external packages needed.  

---

## Security
### **Security Features** :

#### **Password Hashing (SHA-256)**
- **Reason:** Basic security measure to protect user credentials.  
- **Benefit:** Prevents storing plaintext passwords.  

#### **OTP for Order Verification**
- **Reason:** Simple delivery confirmation mechanism.  
- **Benefit:** Reduces potential for delivery fraud or disputes.  

---
