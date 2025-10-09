from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from collections import defaultdict
from database import get_db
from models import User,Expense,Income
from core.security import verify_token

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    
        expenses = db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.date.desc()).all()
        incomes = db.query(Income).filter(Income.user_id == user.id).all()

        total_spent = sum(exp.amount for exp in expenses)
        total_income = sum(inc.amount for inc in incomes)
        recent_expenses = [
            {
                "date": exp.date.strftime("%Y-%m-%d"),
                "category": exp.category,
                "amount": exp.amount,
                "description": exp.description or ""
            }
            for exp in expenses[:5]
        ]

        category_breakdown = {}
        for exp in expenses:
            category_breakdown[exp.category] = category_breakdown.get(exp.category, 0) + exp.amount

        monthly_expenses = defaultdict(float)
        monthly_incomes = defaultdict(float)
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=30)

        for exp in expenses:
            if exp.date >= two_months_ago:
                month_key = exp.date.strftime("%Y-%m")
                monthly_expenses[month_key] += exp.amount

        for inc in incomes:
            if inc.income_date >= two_months_ago:
                month_key = inc.income_date.strftime("%Y-%m")
                monthly_incomes[month_key] += inc.amount

        all_months = set(monthly_expenses.keys()) | set(monthly_incomes.keys())

        monthly_trend = [
            {
                "month": month,
                "income": monthly_incomes.get(month, 0),
                "expense": monthly_expenses.get(month, 0)
            }
            for month in sorted(all_months)
        ]

        monthly_average = total_spent / 2 if expenses else 0

        dashboard_data = {
            "total_spent": total_spent,
            "total_income": total_income,
            "recent_expenses": recent_expenses,
            "category_breakdown": category_breakdown,
            "monthly_trend": monthly_trend,
            "monthly_average": monthly_average
        }
        return JSONResponse(status_code=200, content={"status": "success", "data": dashboard_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error fetching dashboard data: {str(e)}"})
