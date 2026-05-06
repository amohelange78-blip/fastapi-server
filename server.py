from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import time

app = FastAPI()

SECRET = "mysecretkey"

# Fake DB (we upgrade later)
users = {}

# Models
class User(BaseModel):
    username: str
    password: str

# Auth
security = HTTPBearer()

def create_token(username):
    payload = {
        "username": username,
        "exp": time.time() + 3600
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return decoded["username"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
def home():
    return {"message": "Server is running"}

@app.post("/signup")
def signup(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail="User exists")
    users[user.username] = user.password
    return {"message": "User created"}

@app.post("/login")
def login(user: User):
    if users.get(user.username) != user.password:
        raise HTTPException(status_code=401, detail="Invalid login")
    token = create_token(user.username)
    return {"token": token}

@app.get("/trade")
def trade(username: str = Depends(verify_token)):
    return {"message": f"{username} is allowed to trade"}
