# NestNavigate Backend

Backend API for NestNavigate, a gamified learning platform for first-time homebuyers. Built with **FastAPI**, uses **Firebase Firestore** for persistence and JWT for authentication.

## 🚀 Live Demo

- **Frontend (Vercel)**: [https://nestnavigate-frontend.vercel.app](https://nestnavigate-frontend.vercel.app)
- **Backend (Heroku)**: [https://nestnavigate-backend-fb7e09b71ac1.herokuapp.com](https://nestnavigate-backend-fb7e09b71ac1.herokuapp.com)
- **API Docs**: [https://nestnavigate-backend-fb7e09b71ac1.herokuapp.com/docs](https://nestnavigate-backend-fb7e09b71ac1.herokuapp.com/docs)

---

## 🧰 Tech Stack

- **FastAPI** (Python 3.10+)
- **Firebase Firestore** (NoSQL DB)
- **Python-Jose** (JWT Authentication)
- **Passlib** (Password hashing)
- **Pydantic** (Schema validation)
- **Uvicorn** (ASGI server)

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash

git clone https://github.com/mkawak/NestNavigate_Backend.git
cd NestNavigate_Backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set the following environment variable:
export FIREBASE_CONFIG='<your Firebase service account JSON as a single-line string>'

# Run the server locally:
uvicorn main:app --reload
```

---

## 🌐 API Endpoints

### User Management
- `POST /api/users/register` - Register a new user.
- `POST /api/users/login` - User login and token retrieval.
- `GET /api/users/profile` - Retrieve user profile and progress data (requires auth).

### Learning Progress
- `GET /api/modules` - Fetch all learning modules.
- `POST /api/progress/complete-lesson` - Mark a lesson as completed.
- `GET /api/progress/{user_id}` - Retrieve a user’s progress.
- `POST /api/coins/award` - Award coins for a completed activity.


---

## 🕒 Time Spent

- Backend development: **6-8 hours**
  - Setting up FastAPI and auth: 2 hours
  - Building and testing endpoints: 3-4 hours
  - Debugging deployment and Firestore issues: 2 hour