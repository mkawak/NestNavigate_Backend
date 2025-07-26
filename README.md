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