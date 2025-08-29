import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for

# --- Flask Configuration ---
app = Flask(__name__)

# --- Microservice URLs ---
PRODUCT_SERVICE_URL = 'http://product-service:8001/products'
CART_SERVICE_URL = 'http://cart-service:8080/cart'
QUERY_SERVICE_URL = 'http://query-service:8002/query'
# --- HTML Template for the Web Page ---
# (Your HTML_TEMPLATE remains unchanged)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered E-commerce Assistant</title>
    <style>
        body { font-family: sans-serif; max-width: 1000px; margin: auto; padding: 20px; line-height: 1.6; background-color: #f4f4f9; }
        h1, h2 { color: #333; }
        .container { display: flex; gap: 30px; }
        .main-content { flex: 3; }
        .sidebar { flex: 1; }
        .card { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .query-form { display: flex; gap: 10px; }
        .query-input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        .query-button { padding: 10px 20px; border: none; background-color: #007BFF; color: white; border-radius: 4px; cursor: pointer; }
        .query-button:hover { background-color: #0056b3; }
        .response-box { background-color: #e9f5ff; border: 1px solid #b3d7ff; padding: 15px; border-radius: 4px; }
        .response-title { font-weight: bold; margin-bottom: 10px; }
        .product-item, .cart-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding: 10px 0; }
        .product-item:last-child, .cart-item:last-child { border-bottom: none; }
        .add-to-cart-btn { padding: 8px 12px; border: none; background-color: #28a745; color: white; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .add-to-cart-btn:hover { background-color: #218838; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>🛒 AI E-commerce Assistant</h1>
    <div class="container">
        <div class="main-content">
            <div class="card">
                <h2>Ask the Assistant</h2>
                <form class="query-form" method="get" action="/">
                    <input class="query-input" type="text" name="q" placeholder="What is a good laptop for coding?" required value="{{ query or '' }}">
                    <button class="query-button" type="submit">Ask</button>
                </form>
                {% if answer %}
                <div class="response-box" style="margin-top: 20px;">
                    <div class="response-title">Answer:</div>
                    <pre>{{ answer }}</pre>
                </div>
                {% endif %}
                {% if error %}
                <div class="response-box error" style="margin-top: 20px;">
                    <div class="response-title">Error:</div>
                    <p>{{ error }}</p>
                </div>
                {% endif %}
            </div>
            
            <div class="card">
                <h2>Available Products</h2>
                <div class="product-list">
                    {% if products %}
                        {% for product in products %}
                        <div class="product-item">
                            <div>
                                <strong>{{ product.name }}</strong><br>
                                <span>Price: ${{ product.price }}</span>
                            </div>
                            <form method="post" action="/add_to_cart">
                                <input type="hidden" name="productId" value="{{ product.id }}">
                                <input type="hidden" name="name" value="{{ product.name }}">
                                <input type="hidden" name="price" value="{{ product.price }}">
                                <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                            </form>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p>No products available.</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="sidebar">
            <div class="card">
                <h2>Shopping Cart</h2>
                <div class="cart-list">
                    {% if cart_items %}
                        {% for item in cart_items %}
<div class="cart-item">
    <div>
        <span>{{ item.name }}</span><br>
        <strong>${{ item.price }}</strong>
    </div>
    <form method="post" action="/remove_from_cart" style="margin: 0;">
        <input type="hidden" name="itemId" value="{{ item.id }}">
        <button type="submit" class="remove-btn">Remove</button>
    </form>
</div>
{% endfor %}
                    {% else %}
                        <p>Your cart is empty.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """
    Main route for the frontend.
    Handles user input and displays the AI's response, product list, and cart items.
    """
    user_query = request.args.get('q')
    answer = None
    products = []
    cart_items = []
    error = None

    # Step 1: Fetch the product list
    try:
        product_response = requests.get(PRODUCT_SERVICE_URL, timeout=10)
        product_response.raise_for_status()
        products = product_response.json()
    except requests.exceptions.RequestException as e:
        error = f"Could not connect to the Product Service. Is it running? Details: {e}"

    # Step 2: Fetch cart items
    try:
        cart_response = requests.get(CART_SERVICE_URL, timeout=10)
        cart_response.raise_for_status()
        cart_items = cart_response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"Could not connect to the Cart Service. Is it running? Details: {e}"
        error = f"{error}\n{error_msg}" if error else error_msg

    # Step 3: Handle the AI query if one exists
    if user_query:
        print(f"User query received: '{user_query}'")
        try:
            response = requests.get(QUERY_SERVICE_URL, params={'q': user_query}, timeout=30)
            response.raise_for_status() 
            data = response.json()
            answer = data.get('answer')
            if not answer:
                error = data.get('error', 'The query service did not return a valid answer.')
        except requests.exceptions.RequestException as e:
            error = f"Could not connect to the AI Query Service. Please ensure it's running. Details: {e}"
        except Exception as e:
            error = f"An unexpected error occurred: {e}"

    return render_template_string(HTML_TEMPLATE, query=user_query, answer=answer, products=products,cart_items=cart_items, error=error)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """
    Handles removing an item from the cart.
    """
    try:
        item_id = request.form['itemId']
        # The URL for removing from cart is '/cart/remove/{id}'
        response = requests.delete(f"{CART_SERVICE_URL}/remove/{item_id}", timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error removing from cart: {e}")
    
    return redirect(url_for('index'))    

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Handles adding a product to the cart.
    """
    try:
        product_data = {
            'productId': request.form['productId'],
            'name': request.form['name'],
            'price': float(request.form['price'])
        }
        response = requests.post(f"{CART_SERVICE_URL}/add", json=product_data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # In a real app, you'd want to handle this more gracefully (e.g., flash a message)
        print(f"Error adding to cart: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=PORT, debug=True)