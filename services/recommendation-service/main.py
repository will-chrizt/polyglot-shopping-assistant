from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import os
import httpx
import json
from typing import List, Optional, Dict, Any
from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
import boto3
from botocore.exceptions import ClientError
import logging

app = FastAPI(title="Product Recommendation Service")
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bedrock client
try:
    bedrock_client = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    # Initialize LangChain with Bedrock
    llm = BedrockLLM(
        client=bedrock_client,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
except Exception as e:
    logger.error(f"Failed to initialize Bedrock: {e}")
    # Fallback to mock for development
    llm = None

# Request Models
class RecommendationRequest(BaseModel):
    user_preferences: Optional[str] = None
    category: Optional[str] = None
    budget_max: Optional[float] = None
    previous_orders: Optional[List[str]] = None

class ProductQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

# Response Models
class ProductRecommendation(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    tags: List[str]
    recommendation_reason: str
    confidence_score: float

class RecommendationResponse(BaseModel):
    recommendations: List[ProductRecommendation]
    explanation: str
    personalized: bool

# Output Parser for structured recommendations
class RecommendationOutputParser(BaseOutputParser):
    def parse(self, text: str) -> Dict:
        try:
            # Try to extract JSON from the response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback to simple text parsing
                return {"explanation": text, "recommendations": []}
        except json.JSONDecodeError:
            return {"explanation": text, "recommendations": []}

# Prompt Templates
RECOMMENDATION_PROMPT = PromptTemplate(
    input_variables=["products", "user_preferences", "user_info", "previous_orders"],
    template="""
You are an intelligent shopping assistant. Based on the available products and user information, provide personalized product recommendations.

Available Products:
{products}

User Information:
{user_info}

User Preferences: {user_preferences}

Previous Orders: {previous_orders}

Please analyze the products and provide recommendations in the following JSON format:
{{
    "recommendations": [
        {{
            "product_id": "product_id",
            "recommendation_reason": "why this product fits the user's needs",
            "confidence_score": 0.85
        }}
    ],
    "explanation": "Overall explanation of why these products were recommended"
}}

Focus on matching user preferences, considering their budget, and avoiding duplicate categories unless specifically requested.
"""
)

PRODUCT_QUERY_PROMPT = PromptTemplate(
    input_variables=["products", "query", "context"],
    template="""
You are a helpful shopping assistant. Answer the user's question about products based on the available inventory.

Available Products:
{products}

User Query: {query}

Additional Context: {context}

Please provide a helpful, accurate response about the products. If the user is asking for recommendations, suggest specific products with reasons. If they're asking for information, provide detailed and accurate details from the product data.
"""
)

CHAT_PROMPT = PromptTemplate(
    input_variables=["message", "products", "user_context"],
    template="""
You are a friendly shopping assistant chatbot. Help the user with their shopping needs.

Available Products:
{products}

User Context: {user_context}

User Message: {message}

Respond in a helpful, conversational manner. If the user needs product recommendations or has questions about products, use the available product information to provide accurate answers.
"""
)

# Helper Functions
async def get_user_info(token: str) -> Optional[Dict]:
    """Fetch user information from user service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
    return None

async def get_products(category: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Fetch products from product service"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"limit": limit}
            if category:
                params["category"] = category
            
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products", params=params)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
    return []

async def get_user_orders(token: str) -> List[Dict]:
    """Fetch user's previous orders (you'll need to implement this endpoint in order service)"""
    # For now, return empty list as the order service doesn't have a user-specific endpoint
    return []

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None

# Endpoints
@app.get("/")
def root():
    return {"message": "Product Recommendation Service is running"}

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    """Get personalized product recommendations"""
    
    # Verify user token
    user_payload = verify_token(creds.credentials)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user info
    user_info = await get_user_info(creds.credentials)
    if not user_info:
        user_info = {"email": user_payload.get("sub"), "name": user_payload.get("name")}
    
    # Get products
    products = await get_products(category=request.category)
    if not products:
        raise HTTPException(status_code=503, detail="Product service unavailable")
    
    # Get user's previous orders
    previous_orders = await get_user_orders(creds.credentials)
    
    if llm is None:
        # Mock response for development
        mock_recommendations = []
        for i, product in enumerate(products[:3]):
            mock_recommendations.append(ProductRecommendation(
                product_id=product["id"],
                name=product["name"],
                category=product["category"],
                price=product["price"],
                tags=product["tags"],
                recommendation_reason=f"Great choice for your needs - {product['name']} offers excellent value",
                confidence_score=0.85 - (i * 0.1)
            ))
        
        return RecommendationResponse(
            recommendations=mock_recommendations,
            explanation="These products are recommended based on your preferences and available inventory.",
            personalized=True
        )
    
    # Create LangChain chain
    chain = LLMChain(
        llm=llm,
        prompt=RECOMMENDATION_PROMPT,
        output_parser=RecommendationOutputParser()
    )
    
    try:
        # Generate recommendations
        result = await chain.arun(
            products=json.dumps(products, indent=2),
            user_preferences=request.user_preferences or "No specific preferences",
            user_info=json.dumps(user_info, indent=2),
            previous_orders=json.dumps(previous_orders, indent=2)
        )
        
        # Process the result
        recommendations = []
        if isinstance(result, dict) and "recommendations" in result:
            for rec in result["recommendations"]:
                # Find the product details
                product = next((p for p in products if p["id"] == rec["product_id"]), None)
                if product:
                    recommendations.append(ProductRecommendation(
                        product_id=product["id"],
                        name=product["name"],
                        category=product["category"],
                        price=product["price"],
                        tags=product["tags"],
                        recommendation_reason=rec.get("recommendation_reason", "Recommended for you"),
                        confidence_score=rec.get("confidence_score", 0.8)
                    ))
        
        return RecommendationResponse(
            recommendations=recommendations,
            explanation=result.get("explanation", "Recommendations based on your preferences"),
            personalized=True
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@app.post("/query")
async def query_products(request: ProductQueryRequest):
    """Answer natural language queries about products"""
    
    # Get products
    products = await get_products()
    if not products:
        raise HTTPException(status_code=503, detail="Product service unavailable")
    
    if llm is None:
        # Mock response for development
        return {
            "answer": f"Based on your query '{request.query}', here are some relevant products from our catalog.",
            "products": products[:3]
        }
    
    # Create LangChain chain
    chain = LLMChain(llm=llm, prompt=PRODUCT_QUERY_PROMPT)
    
    try:
        result = await chain.arun(
            products=json.dumps(products, indent=2),
            query=request.query,
            context=json.dumps(request.context or {}, indent=2)
        )
        
        return {"answer": result, "products": products}
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.post("/chat")
async def chat(
    request: ChatRequest,
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    """Chat interface for shopping assistance"""
    
    # Verify user token
    user_payload = verify_token(creds.credentials)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user info and products
    user_info = await get_user_info(creds.credentials)
    products = await get_products()
    
    if llm is None:
        # Mock response for development
        return {
            "response": f"Hello! I'd be happy to help you with your shopping. You asked: '{request.message}'. How can I assist you with finding the right products?",
            "conversation_id": request.conversation_id or "mock-conversation-id"
        }
    
    # Create LangChain chain
    chain = LLMChain(llm=llm, prompt=CHAT_PROMPT)
    
    try:
        result = await chain.arun(
            message=request.message,
            products=json.dumps(products, indent=2),
            user_context=json.dumps(user_info or {}, indent=2)
        )
        
        return {
            "response": result,
            "conversation_id": request.conversation_id or f"conv-{user_payload.get('sub')}"
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bedrock_available": llm is not None,
        "services": {
            "product_service": PRODUCT_SERVICE_URL,
            "user_service": USER_SERVICE_URL
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))
