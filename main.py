# Created by Majd Kawak 07/25/2025

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# --- Initialize FastAPI ---
app = FastAPI()

# --- CORS middleware for React frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Initialization ---
print("Initializing Firebase from environment variable...")
firebase_creds_json = os.getenv("FIREBASE_KEY")
if not firebase_creds_json:
    raise RuntimeError("FIREBASE_KEY environment variable not set")

firebase_creds = json.loads(firebase_creds_json)
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred)
db = firestore.client()
print("Firebase initialized")

# --- JWT Configuration ---
SECRET_KEY = "kTrXtbjOas4k-Xz9YbT4zt3u8mhujnWCKXyN6kEf4UQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Security / Password ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# --- Firestore Collections ---
users_db = db.collection("users")
modules_db = db.collection("modules")
progress_db = db.collection("progress")

# --- Sample Modules ---
sample_modules = [
    {
        "id": "mod_1",
        "title": "Home Buying Basics",
        "lessons": ["What is a Mortgage?", "Down Payments 101", "Credit Scores"],
        "total_coins": 75,
        "difficulty": "Beginner"
    },
    {
        "id": "mod_2",
        "title": "Home Inspections",
        "lessons": ["Types of Inspections", "Common Issues Found", "Hiring an Inspector"],
        "total_coins": 100,
        "difficulty": "Intermediate"
    },
    {
        "id": "mod_3",
        "title": "Mortgage Types",
        "lessons": ["Fixed vs Adjustable Rates", "FHA, VA, and Conventional Loans", "Interest Rates Explained"],
        "total_coins": 90,
        "difficulty": "Intermediate"
    },
    {
        "id": "mod_4",
        "title": "Closing Process",
        "lessons": ["What to Expect on Closing Day", "Closing Costs Breakdown", "Title and Escrow"],
        "total_coins": 85,
        "difficulty": "Beginner"
    },
    {
        "id": "mod_5",
        "title": "Homeownership Responsibilities",
        "lessons": ["Maintenance Basics", "Property Taxes", "HOA Rules"],
        "total_coins": 70,
        "difficulty": "Beginner"
    }
]

# --- Defer Module Initialization ---
@app.on_event("startup")
async def init_modules():
    print("Checking modules in Firestore...")
    existing = list(modules_db.stream())
    if not existing:
        print("No modules found. Creating default modules.")
        for module in sample_modules:
            modules_db.document(module["id"]).set(module)
        print("Sample modules initialized.")
    else:
        print(f"{len(existing)} modules already exist.")

# --- Models ---
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    coins_earned: int = 0
    created_at: datetime

class Module(BaseModel):
    id: str
    title: str
    lessons: List[str]
    total_coins: int
    difficulty: str

class Progress(BaseModel):
    user_id: int
    module_id: str
    lessons_completed: List[str]
    completion_percentage: float
    last_accessed: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Utility Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(email: str):
    query = users_db.where("email", "==", email).limit(1).stream()
    for doc in query:
        return doc.to_dict()
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- API Endpoints ---

@app.post("/api/users/register")
def register(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(len([*users_db.stream()]) + 1)
    hashed_password = get_password_hash(user.password)
    users_db.document(user_id).set({
        "id": int(user_id),
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "coins_earned": 0,
        "created_at": datetime.utcnow().isoformat(),
    })
    return {"msg": "User registered successfully"}

@app.post("/api/users/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/profile", response_model=User)
def get_profile(current_user: dict = Depends(get_current_user)):
    return User(**current_user)

@app.get("/api/modules", response_model=List[Module])
def get_modules():
    return [doc.to_dict() for doc in modules_db.stream()]

@app.post("/api/progress/complete-lesson")
def complete_lesson(user_id: int, module_id: str, lesson: str):
    doc_id = f"{user_id}_{module_id}"
    doc_ref = progress_db.document(doc_id)
    doc = doc_ref.get()
    lessons_completed = []

    if doc.exists:
        progress = doc.to_dict()
        lessons_completed = progress["lessons_completed"]
        if lesson not in lessons_completed:
            lessons_completed.append(lesson)
    else:
        lessons_completed = [lesson]

    module_doc = modules_db.document(module_id).get()
    if not module_doc.exists:
        raise HTTPException(status_code=404, detail="Module not found")
    module_data = module_doc.to_dict()

    completion_percentage = len(lessons_completed) / len(module_data["lessons"]) * 100
    doc_ref.set({
        "user_id": user_id,
        "module_id": module_id,
        "lessons_completed": lessons_completed,
        "completion_percentage": completion_percentage,
        "last_accessed": datetime.utcnow().isoformat()
    })

    # Reward logic
    if completion_percentage == 100:
        module_coins = module_data.get("total_coins", 0)
        user_docs = users_db.where("id", "==", user_id).limit(1).stream()
        user_doc = next(user_docs, None)
        if user_doc:
            user_data = user_doc.to_dict()
            rewarded_modules = user_data.get("rewarded_modules", {})
            if not rewarded_modules.get(module_id):
                new_total = user_data.get("coins_earned", 0) + module_coins
                rewarded_modules[module_id] = True
                users_db.document(user_doc.id).update({
                    "coins_earned": new_total,
                    "rewarded_modules": rewarded_modules
                })

    return {"msg": "Lesson marked as completed"}

@app.get("/api/progress/{user_id}", response_model=List[Progress])
def get_progress(user_id: int):
    return [doc.to_dict() for doc in progress_db.where("user_id", "==", user_id).stream()]

@app.post("/api/coins/award")
def award_coins(user_id: int, coins: int):
    user_docs = users_db.where("id", "==", user_id).limit(1).stream()
    user_doc = next(user_docs, None)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_doc.to_dict()
    new_total = user_data.get("coins_earned", 0) + coins
    users_db.document(user_doc.id).update({"coins_earned": new_total})
    return {"msg": f"{coins} coins awarded"}