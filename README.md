# Diabetes Prediction Using Machine Learning

An MCA Final-Year Project & Research Framework built with **React**, **FastAPI**, **SQLAlchemy**, **MySQL**, **XGBoost**, and **ReportLab**. Implements zero-shot external dataset validation (Pima → Mendeley, $n=1,168$), demographic subgroup fairness analysis, probability calibration, and TRIPOD-AI standardized reporting.

---

## 📁 Project Architecture & File Structure

```text
smart-healthcare-assistant/
│
├── frontend/                     # React.js + Vite Frontend Application
│   ├── src/
│   │   ├── components/           # Layout, Navbar, Sidebar, ProtectedRoute
│   │   ├── pages/                # Login, Register, Dashboard
│   │   ├── services/             # Axios API Service & Interceptors
│   │   ├── context/              # AuthContext (JWT & User state)
│   │   ├── hooks/                # useAuth custom hook
│   │   ├── utils/                # Utility helpers
│   │   ├── App.jsx               # React Router Configuration
│   │   ├── App.css               # Component layout styles
│   │   ├── index.css             # Healthcare design system tokens
│   │   └── main.jsx              # React Entrypoint
│   ├── .env                      # Frontend environment configuration
│   ├── .env.example              # Frontend environment template
│   ├── index.html                # HTML entrypoint with Inter font
│   ├── vite.config.js            # Vite configuration
│   └── package.json              # React dependencies
│
├── backend/                      # Python FastAPI Backend API
│   ├── app/
│   │   ├── main.py               # FastAPI App, CORS, & Startup
│   │   ├── database/             # SQLAlchemy Engine & Session manager
│   │   ├── models/               # SQLAlchemy User Model
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── routes/               # Health and Auth endpoints
│   │   ├── services/             # Patient registration & authentication logic
│   │   └── utils/                # Bcrypt password hashing & PyJWT security
│   ├── test_db.py                # Database connection test script
│   ├── init_db.py                # Database table initialization script
│   ├── requirements.txt          # Python backend dependencies
│   ├── .env                      # Backend environment configuration
│   └── .env.example              # Backend environment template
│
├── ml/                           # Machine Learning Module Structure
│   ├── datasets/                 # Datasets placeholder
│   ├── training/                 # Model training scripts placeholder
│   ├── preprocessing/            # Data preprocessing pipelines placeholder
│   ├── evaluation/               # Model evaluation scripts placeholder
│   └── models/                   # Serialized ML models placeholder
│
├── database/
│   └── schema.sql                # MySQL Database DDL Schema
│
├── README.md                     # Complete Setup & Execution Documentation
└── .gitignore                    # Git ignore rules for Python & Node
```

---

## 🛠️ Technology Stack

- **Frontend**: React.js 18, Vite, JavaScript, Axios, React Router v6, Lucide Icons, Custom CSS
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, Bcrypt
- **Database**: MySQL (supported via `pymysql` driver) / SQLite fallback option
- **Machine Learning**: Python, Scikit-learn, Pandas, NumPy, XGBoost (prepared architecture)

---

## ⚡ Quick Start Guide

### 1. Backend Setup & Run

Navigate to the `backend/` directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Initialize the Database tables:

```bash
python init_db.py
```

Test Database Connectivity:

```bash
python test_db.py
```

Start the FastAPI backend server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- **API Root**: `http://127.0.0.1:8000/`
- **Health Check**: `http://127.0.0.1:8000/api/health`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup & Run

Navigate to the `frontend/` directory:

```bash
cd frontend
```

Install dependencies:

```bash
cmd /c npm install
```

Start the Vite development server:

```bash
cmd /c npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🗄️ How to Configure MySQL Database

1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or `mysql` CLI).
2. Create the database:
   ```sql
   CREATE DATABASE smart_healthcare_db;
   ```
3. Import the initial SQL schema:
   ```bash
   mysql -u root -p smart_healthcare_db < database/schema.sql
   ```
4. Open `backend/.env` and update the `DATABASE_URL`:
   ```env
   DATABASE_URL=mysql+pymysql://<YOUR_MYSQL_USER>:<YOUR_MYSQL_PASSWORD>@localhost:3306/smart_healthcare_db
   ```
5. Re-run `python test_db.py` to confirm the MySQL connection works!

---

## 🧪 How to Test Part 0 & Part 1 Authentication Flow

1. **Verify Backend Status**:
   - Open `http://localhost:5173/login`. Look at the Navbar header. It should display **Backend Status: Connected** with a pulsing green indicator.

2. **Test Patient Registration (`/register`)**:
   - Navigate to `http://localhost:5173/register`.
   - Fill in Full Name, Email, Phone, Age, Gender, Password, and Confirm Password.
   - Click **Register Patient Account**.
   - Verify success alert and auto-redirection to `/login`.
   - Try registering again with the **same email** -> verify duplicate email rejection error banner.

3. **Test Patient Login (`/login`)**:
   - Enter invalid credentials -> verify error alert.
   - Enter valid registered credentials -> click **Sign In**.
   - Verify redirect to `/dashboard`.

4. **Test Protected Dashboard (`/dashboard`)**:
   - Verify welcome banner displaying the patient's name, email, age, gender, and **PATIENT** role badge.
   - Verify active session indicator and system overview cards.

5. **Test Protected Route Guard**:
   - Log out using the **Logout** button.
   - Try directly accessing `http://localhost:5173/dashboard` in the address bar -> verify automatic redirect to `/login`.

---

## 🔒 Security Summary

- Password hashing is enforced via **Bcrypt**.
- Authentication tokens are signed using **PyJWT** (HS256) with expiration handling.
- Input models are strictly validated via **Pydantic**.
- Backend routes use `Depends(get_current_user)` for token verification.
