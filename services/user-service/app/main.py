from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt, time, os


app = FastAPI(title="User Service")
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")


class RegisterReq(BaseModel):
email: str
password: str
name: str


USERS = {}


@app.post("/register", status_code=201)
def register(req: RegisterReq):
if req.email in USERS:
raise HTTPException(status_code=409, detail="Email exists")
USERS[req.email] = {"email": req.email, "password": req.password, "name": req.name, "id": len(USERS)+1}
return {"ok": True}


class LoginReq(BaseModel):
email: str
password: str


@app.post("/login")
def login(req: LoginReq):
u = USERS.get(req.email)
if not u or u["password"] != req.password:
raise HTTPException(status_code=401, detail="Invalid creds")
payload = {"sub": u["email"], "name": u["name"], "iat": int(time.time())}
token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
return {"token": token}


@app.get("/me")
def me(creds: HTTPAuthorizationCredentials = Depends(security)):
try:
payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
except Exception:
raise HTTPException(status_code=401, detail="Invalid token")
email = payload["sub"]
return USERS.get(email, {})
