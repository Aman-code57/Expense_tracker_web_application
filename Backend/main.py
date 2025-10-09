from fastapi import FastAPI
from database import engine
from models import Base
from api.auth import router as auth_router
from api.dashboard import router as dashboard_router
from api.income import router as income_router
from api.expense import router as expense_router
from middleware.cors import add_cors_middleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API", version="1.0.0")

add_cors_middleware(app)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(dashboard_router)
app.include_router(income_router)
app.include_router(expense_router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Expense Tracker API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
