# FILE: frontend-service.py
# This is the new frontend microservice.
# It provides a web interface for the user to interact with the query-service.
# -----------------------------------------------------------------------------

import os
import requests
from flask import Flask, render_template_string, request

# --- Flask Configuration ---
app = Flask(__name__)

# --- Microservice Ports ---
# Define the port for the query service to make API calls to.
QUERY_SERVICE_PORT = 8002

# The URL of the query microservice.
QUERY_SERVICE_URL = f'http://localhost:{QUERY_SERVICE_PORT}/query'

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
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """
    Main route for the frontend.
    Handles user input and displays the AI's response.
    """
    user_query = request.args.get('q')
    answer = None
    error = None

    if user_query:
        print(f"User query received: '{user_query}'")
        try:
            # Call the query service API
            response = requests.get(QUERY_SERVICE_URL, params={'q': user_query}, timeout=30)
            
            # Raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status() 

            # Parse the JSON response
            data = response.json()
            answer = data.get('answer')
            if not answer:
                error = data.get('error', 'The query service did not return a valid answer.')

        except requests.exceptions.RequestException as e:
            error = f"Could not connect to the AI Query Service. Please ensure it's running. Details: {e}"
        except Exception as e:
            error = f"An unexpected error occurred: {e}"

    return render_template_string(HTML_TEMPLATE, query=user_query, answer=answer, error=error)

if __name__ == '__main__':
    # Define the port from an environment variable or default to 8000
    PORT = int(os.environ.get('PORT', 8000))
    app.run(debug=True, port=PORT)
    print(f"🚀 Flask frontend service running on http://localhost:{PORT}")
    print(f"🔗 Access the application here: http://localhost:{PORT}")
