# Inventory Management System

## Description
This is a simple inventory management system built using Flask and SQLite. It allows users to:
- Add, edit, and delete products
- Manage product stock
- Process transactions
- Manage a shopping cart
- View transaction history

## Features
- Flask-based web application
- SQLite database for data storage
- User-friendly interface for managing inventory and transactions
- Image upload for products
- Shopping cart functionality
- Transaction history tracking

## Requirements
Before running the application, ensure you have the following installed:
- Python 3.x

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/MizukiHikari/mizu-market
   cd mizu-market
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Application
1. Start the Flask application:
   ```sh
   python app.py
   ```
2. Open your browser and go to:
   ```
   http://127.0.0.1:6969/
   ```

## Configuration
- Database: SQLite (`inventory.db`)
- Image Uploads: Stored in `static/uploads/`
- Default Flask Debug Mode: `True`

## API Endpoints
### Product Management
- `POST /add_product` - Add a new product
- `GET /get_product/<product_id>` - Retrieve product details
- `POST /edit_product/<product_id>` - Edit product details
- `GET /delete_product/<product_id>` - Delete a product

### Shopping Cart
- `POST /add_to_cart/<product_id>` - Add a product to the cart
- `POST /remove_from_cart/<item_id>` - Remove a product from the cart
- `POST /checkout` - Process checkout

### Transaction Management
- `POST /delete_transaction/<transaction_id>` - Delete a transaction
- `GET /view_transaction/<transaction_id>` - View transaction details

## License
This project is licensed under the MIT License.


