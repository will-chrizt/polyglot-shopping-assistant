To start your application, you'll need to run each of the three microservices in separate terminal windows. Make sure you've completed the setup (installing dependencies) for each service first.

▶️ How to Run the Application
Follow these steps to get all services operational:

Start the Product Service (Node.js)
This service runs on Port 8001.
In your first terminal window, navigate to the directory containing product-service.js and execute:

Bash

node product-service.js
You should see a confirmation message indicating that the product service is running.

Start the Query Service (Node.js)
This service runs on Port 8002 and requires AWS credentials.
In your second terminal window, navigate to the directory containing query-service.js. Before running, ensure your AWS environment variables are set:

Bash

# Set these environment variables in your terminal session


export AWS_REGION="your-aws-region" # e.g., us-east-1
export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"

# Then, run the service:
node query-service.js

# Then, run the service:
node query-service.js
A message confirming the AI Query service is running should appear.

Start the Frontend Service (Flask)
This service runs on Port 8000.
In your third terminal window, navigate to the directory containing frontend-service.py and execute:

Bash

python frontend-service.py
You'll see a confirmation that the Flask frontend service is running.

🌐 Accessing the Application
Once all three services are running successfully, open your web browser and navigate to:

http://localhost:8000

You should now see the frontend with the list of products and the query input field.
