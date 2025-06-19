from fastapi import FastAPI
from database import engine, Base
from routers import auth, accounts, categories, transactions

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wallet API",
    description="API for the Wallet personal finance tracker.",
    version="0.1.0"
)

app.include_router(auth.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wallet API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
