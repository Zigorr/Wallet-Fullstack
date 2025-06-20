from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, accounts, categories, transactions, recurring_transactions

# Create all tables (for development)
# Tables will be created only if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wallet API",
    description="API for the Wallet personal finance tracker.",
    version="0.1.0"
)

# CORS Middleware - Very permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add explicit OPTIONS handler for all routes
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )



app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(recurring_transactions.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wallet API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
