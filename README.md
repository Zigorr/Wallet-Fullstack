# Wallet - Personal Finance Tracker

A modern, clean personal finance tracking application built with React and FastAPI. Features a beautiful dark theme UI with glassmorphism effects and real-time financial analytics.

## Features

### 🎨 Modern UI/UX
- Clean, dark theme interface optimized for desktop
- Glassmorphism effects with backdrop blur
- Smooth animations and transitions with Framer Motion
- Responsive design with Tailwind CSS
- Beautiful charts and visualizations

### 💰 Financial Management
- **Dashboard**: Financial overview with key metrics and analytics
- **Accounts**: Manage multiple account types (Checking, Savings, Credit, Investment, Cash)
- **Transactions**: Track income, expenses, and transfers with categorization
- **Categories**: Organize transactions with custom colored categories
- **Analytics**: Visual insights into spending patterns and financial health
- **Settings**: User preferences and account management

### 🔐 Security
- JWT-based authentication
- Password validation with regex patterns
- Secure API endpoints with CORS protection
- Protected routes and authentication guards

### 📊 Analytics
- Real-time balance calculations
- Monthly income vs expenses tracking
- Savings rate monitoring
- Account breakdown visualizations
- Category-based spending analysis
- Recent transaction history

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **TanStack React Query** for data fetching
- **React Router DOM** for navigation
- **Recharts** for data visualizations
- **Heroicons** for icons
- **Axios** for API calls

### Backend
- **FastAPI** with Python
- **SQLAlchemy** for ORM
- **Alembic** for database migrations
- **JWT** for authentication
- **Pydantic** for data validation
- **SQLite** database
- **Passlib** for password hashing

## Installation

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Wallet/Wallet-Backend
```

2. Create a virtual environment:
```bash
python -m venv wallet
```

3. Activate the virtual environment:
```bash
# Windows
wallet\Scripts\activate
# macOS/Linux
source wallet/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the backend server:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ../Wallet-Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Register a new account or log in with existing credentials
3. Create your first account to start tracking finances
4. Add transactions and categories to organize your financial data
5. View analytics and insights on the dashboard

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login and get access token
- `GET /api/auth/users/me` - Get current user info

### Accounts
- `GET /api/accounts/` - Get user accounts
- `POST /api/accounts/` - Create new account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account

### Transactions
- `GET /api/transactions/` - Get user transactions
- `POST /api/transactions/` - Create new transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Categories
- `GET /api/categories/` - Get user categories
- `POST /api/categories/` - Create new category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

## Project Structure

```
Wallet/
├── Wallet-Backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── database.py          # Database configuration
│   ├── config.py            # App configuration
│   ├── dependencies.py      # Common dependencies
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       ├── auth.py          # Authentication routes
│       ├── accounts.py      # Account management
│       ├── transactions.py  # Transaction management
│       └── categories.py    # Category management
└── Wallet-Frontend/
    ├── src/
    │   ├── components/      # Reusable UI components
    │   ├── contexts/        # React contexts
    │   ├── models/          # TypeScript interfaces
    │   ├── pages/           # Page components
    │   ├── services/        # API service layer
    │   ├── utils/           # Utility functions
    │   ├── App.tsx          # Main app component
    │   └── main.tsx         # App entry point
    ├── package.json         # Node dependencies
    └── tailwind.config.js   # Tailwind configuration
```

## Configuration

### Backend Configuration
The backend uses environment variables for configuration. Create a `.env` file in the `Wallet-Backend` directory:

```env
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
PASSWORD_REGEX=^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$
PASSWORD_MESSAGE=Password must be at least 8 characters long and contain both letters and numbers
```

### Frontend Configuration
The frontend API base URL can be configured in `src/services/api.ts`:

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});
```

## Development

### Running Tests
```bash
# Backend tests
cd Wallet-Backend
python -m pytest

# Frontend tests
cd Wallet-Frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd Wallet-Frontend
npm run build

# Backend deployment
cd Wallet-Backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Modern UI design inspired by contemporary fintech applications
- Icons provided by Heroicons
- Charts powered by Recharts
- Animations by Framer Motion 