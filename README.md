# Wallet Backend API 💰

A modern Python FastAPI backend for personal finance management, similar to Budget Bakers Wallet.

## 🚀 Features

- ✅ **User Authentication** (JWT-based)
- ✅ **Account Management** (Bank accounts, credit cards, etc.)
- ✅ **Transaction Tracking** (Income, expenses, transfers)
- ✅ **Budget Management** (Daily, weekly, monthly budgets)
- ✅ **Category System** (Expense categorization)
- ✅ **RESTful API** with automatic documentation
- ✅ **PostgreSQL Database** with async support
- ✅ **Free hosting compatible** (Railway, Render, etc.)

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+ 
- PostgreSQL database
- Git

### 1. Clone and Setup Environment

```bash
# Navigate to backend directory
cd Wallet-Backend

# Create virtual environment
python -m venv wallet_env

# Activate virtual environment
# Windows:
wallet_env\Scripts\activate
# Mac/Linux:
source wallet_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL locally
# Create database
createdb wallet_db
```

#### Option B: Free Cloud Database (Recommended)
- **Supabase**: https://supabase.com (Free 500MB)
- **Neon**: https://neon.tech (Free 3GB)
- **Railway**: https://railway.app (Free PostgreSQL)

### 3. Environment Configuration

```bash
# Copy example environment file
cp env.example .env

# Edit .env file with your settings
# Required settings:
DATABASE_URL=postgresql://username:password@localhost:5432/wallet_db
SECRET_KEY=your-super-secret-key-here
```

### 4. Run the Application

```bash
# Start the development server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Accounts
- `GET /api/v1/accounts` - List user accounts
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

### Transactions
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction

### Budgets & Categories
- `GET /api/v1/budgets` - List budgets
- `GET /api/v1/categories` - List categories

## 🧪 Testing the API

### Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "password123",
       "first_name": "John",
       "last_name": "Doe"
     }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "password123"
     }'
```

## 🌍 Free Deployment Options

### Railway (Recommended)
1. Connect GitHub repository
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy automatically

### Render
1. Connect GitHub repository  
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

### Fly.io
```bash
# Install Fly CLI
# In project directory:
fly launch
fly deploy
```

## 🔧 Development

### Database Migrations (Future)
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Project Structure
```
Wallet-Backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core functionality
│   ├── models/               # Database models
│   └── schemas/              # Pydantic schemas
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies
└── env.example              # Environment template
```

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS protection
- Rate limiting
- Input validation
- SQL injection prevention

## 🎯 Next Steps

1. **Frontend Integration**: Connect with React frontend
2. **Complete CRUD Operations**: Finish all endpoint implementations
3. **Bank Integration**: Add Plaid for automatic transaction sync
4. **Analytics**: Add spending insights and reports
5. **Mobile Apps**: Extend to React Native/Flutter

---

🚀 **Ready to build your personal finance app!** The foundation is set up and working.
