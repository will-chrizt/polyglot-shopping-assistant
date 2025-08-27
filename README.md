# 🛒 AI-Powered E-commerce Assistant

This project is a full-stack microservice application that combines AI-powered product recommendations with a dynamic product catalog. It includes:

- **Frontend Service**: Flask-based UI for user interaction  
- **Query Service**: AI assistant powered by AWS Bedrock  
- **Product Service**: REST API serving product data  

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/willchrist/ai-ecommerce-assistant.git
cd ai-ecommerce-assistant

Create a .env File
Add your AWS credentials and service ports:

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

PORT_PRODUCT=8001
QUERY_SERVICE_PORT=8002
Never commit .env to version control. Add it to .gitignore.

This will start:

product-service on port 8001

query-service on port 8002

frontend-service on port 8000

Open your browser and visit:

Code
http://localhost:8000



[Frontend Service] <---> [Query Service] <---> [AWS Bedrock]
        |
        v
[Product Service] <---> [MongoDB or Static JSON]
