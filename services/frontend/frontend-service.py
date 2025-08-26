# FILE: frontend-service.py

import os
import requests
from flask import Flask, render_template_string, request

# --- Flask Configuration ---
app = Flask(__name__)

# --- Microservice Ports ---
# Define the ports for the query and product services.
QUERY_SERVICE_PORT = 8002
PRODUCT_SERVICE_PORT = 8001

# The URLs of the microservices.
QUERY_SERVICE_URL = f'http://localhost:{QUERY_SERVICE_PORT}/query'
PRODUCT_SERVICE_URL = f'http://localhost:{PRODUCT_SERVICE_PORT}/products'

# --- HTML Template for the Web Page ---
# This is a simple HTML template for the user interface.
# It includes a form for the query and a section to display the answer.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered E-commerce Assistant</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; line-height: 1.6; }
        h1 { text-align: center; color: #333; }
        .container { background-color: #f9f9f9; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .query-form { display: flex; gap: 10px; margin-bottom: 20px; }
        .query-input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        .query-button { padding: 10px 20px; border: none; background-color: #007BFF; color: white; border-radius: 4px; cursor: pointer; }
        .query-button:hover { background-color: #0056b3; }
        .response-box { background-color: white; border: 1px solid #ddd; padding: 15px; border-radius: 4px; }
        .response-title { font-weight: bold; margin-bottom: 10px; }
        .product-list { margin-top: 30px; }
        .product-item { background-color: white; border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 4px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 AI E-commerce Assistant</h1>
        <form class="query-form" method="get" action="/">
            <input class="query-input" type="text" name="q" placeholder="What is a good laptop for coding?" required value="{{ query or '' }}">
            <button class="query-button" type="submit">Ask the Assistant</button>
        </form>
        {% if answer %}
        <div class="response-box">
            <div class="response-title">Answer:</div>
            <pre>{{ answer }}</pre>
        </div>
        {% endif %}
        {% if error %}
        <div class="response-box error">
            <div class="response-title">Error:</div>
            <p>{{ error }}</p>
        </div>
        {% endif %}
        
        <div class="product-list">
            <h2>Available Products</h2>
            {% if products %}
            {% for product in products %}
            <div class="product-item">
                <strong>{{ product.name }}</strong><br>
                Price: ${{ product.price }}
            </div>
            {% endfor %}
            {% else %}
            <p>No products available.</p>
            {% endif %}
        </div>

    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """
    Main route for the frontend.
    Handles user input and displays the AI's response and product list.
    """
    user_query = request.args.get('q')
    answer = None
    products = []
    error = None

    # Step 1: Fetch the product list first
    try:
        product_response = requests.get(PRODUCT_SERVICE_URL, timeout=10)
        product_response.raise_for_status()
        products = product_response.json()
    except requests.exceptions.RequestException as e:
        error = f"Could not connect to the Product Service. Is it running? Details: {e}"

    # Step 2: Handle the AI query if one exists
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

    return render_template_string(HTML_TEMPLATE, query=user_query, answer=answer, products=products, error=error)

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    app.run(debug=True, host=HOST, port=PORT)
    print(f"🚀 Flask frontend service running on {HOST}:{PORT}")
    print(f"🔗 Access the application here (if exposed): http://<your-host-or-service-name>:${PORT}")

