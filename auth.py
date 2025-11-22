from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from database import get_db
from models import User

router = APIRouter()

SECRET_KEY = "MY_SECRET"
ALGORITHM = "HS256"
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

# ---------------------------
# Helper to avoid bcrypt 72 byte limit
# ---------------------------
def bcrypt_safe(password: str) -> str:
    """
    Truncate password to 72 characters to avoid bcrypt errors.
    """
    return password[:72]

# ---------------------------
# JWT helpers
# ---------------------------
def create_token(user: User):
    data = {
        "id": user.id,
        "is_admin": user.is_admin,  # add admin flag here
        "exp": datetime.utcnow() + timedelta(hours=5)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(401, "Invalid token")

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user = db.query(User).filter(User.id == payload["id"]).first()
    if not user:
        raise HTTPException(401, "User not found")
    user.is_admin = payload.get("is_admin", False)  # attach admin info
    return user

def admin_required(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admins only")
    return user

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")

    hashed = pwd.hash(bcrypt_safe(password))  # truncate password
    user = User(email=email, password=hashed, is_admin=False)
    db.add(user)
    db.commit()
    return {"message": "Registered"}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not pwd.verify(bcrypt_safe(form.password), user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user)  # pass the User object
    return {"accessToken": token}
