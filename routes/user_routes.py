from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import db

router = APIRouter()

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# SIGNUP
@router.post("/signup")
def signup(user: UserSignup):

    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db.users.insert_one({
        "name": user.name,
        "email": user.email,
        "password": user.password
    })

    return {"message": "User created successfully"}


# LOGIN
@router.post("/login")
def login(user: UserLogin):

    db_user = db.users.find_one({
        "email": user.email,
        "password": user.password
    })

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "name": db_user["name"],
        "email": db_user["email"]
    }