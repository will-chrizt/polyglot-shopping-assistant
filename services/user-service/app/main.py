from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt, time, os

app = FastAPI(title="User Service")
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")

# 🧾 Request model for registration
class RegisterReq(BaseModel):
    email: str
    password: str
    name: str

# 🧾 Request model for login
class LoginReq(BaseModel):
    email: str
    password: str

# 🗂️ In-memory user store
USERS = {}

# 🚀 Register endpoint
@app.post("/register", status_code=201)
def register(req: RegisterReq):
    if req.email in USERS:
        raise HTTPException(status_code=409, detail="Email exists")
    USERS[req.email] = {
        "email": req.email,
        "password": req.password,
        "name": req.name,
        "id": len(USERS) + 1
    }
    return {"ok": True}

# 🔐 Login endpoint
@app.post("/login")
def login(req: LoginReq):
    u = USERS.get(req.email)
    if not u or u["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid creds")
    payload = {
        "sub": u["email"],
        "name": u["name"],
        "iat": int(time.time())
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"token": token}

# 🙋‍♂️ Authenticated user info
@app.get("/me")
def me(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException

@app.get("/")
def root():
    return {"message": "User Service is running"}

