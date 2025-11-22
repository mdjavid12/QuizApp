from fastapi import FastAPI
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext
from auth import router as auth_router
from questions import router as questions_router
from quiz import router as quiz_router

app = FastAPI()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Include routers
app.include_router(auth_router)
app.include_router(questions_router)
app.include_router(quiz_router)

# --------------------------------------
# Create database tables
# --------------------------------------
Base.metadata.create_all(bind=engine)

# --------------------------------------
# Create default admin user on startup
# --------------------------------------
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"  # you can change this

def create_admin_user():
    db: Session = next(get_db())
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        hashed = pwd.hash(ADMIN_PASSWORD[:72])  # safe for bcrypt
        admin = User(email=ADMIN_EMAIL, password=hashed, is_admin=True)
        db.add(admin)
        db.commit()
        print(f"Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    else:
        print("Admin user already exists")

create_admin_user()
