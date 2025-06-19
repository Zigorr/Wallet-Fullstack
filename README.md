# Wallet: Personal Finance Tracker

This is a full-stack personal finance tracking application, similar to Wallet by BudgetBakers. It includes a Python backend, a React frontend, and a planned React Native mobile app.

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy with Alembic for migrations
- PostgreSQL
- Pydantic for data validation
- `requirements.txt` for dependency management

### Frontend
- React
- TypeScript
- Vite
- `package.json` for dependency management

## Project Structure
```
Wallet/
├── Wallet-Backend/
│   ├── alembic/
│   ├── routers/
│   ├── alembic.ini
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── Wallet-Frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd Wallet-Backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file** in the `Wallet-Backend` directory and add the following environment variables. Replace the values with your PostgreSQL database credentials.
    ```
    DATABASE_URL=postgresql://user:password@hostname:port/database_name
    SECRET_KEY=your_super_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```
    **Note:** If your password contains special characters like `@`, it must be URL-encoded. For example, `p@ssword` becomes `p%40ssword`.

5.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd Wallet-Frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`. 