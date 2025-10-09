from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User,Income
from core.security import verify_token
from crud.income_crud import get_incomes as crud_get_incomes, create_income as crud_create_income, update_income as crud_update_income, delete_income as crud_delete_income

router = APIRouter()

@router.get("/income")
async def get_incomes_safe(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        incomes = crud_get_incomes(db, user.id)
        income_list = []
            
        for inc in incomes:
            try:
                    
                    source = inc.source or ""
                    amount = float(inc.amount)if inc.amount else 0.0
                    description = inc.description or ""
                    income_date_str = ""
                    if inc.income_date:
                        try:
                            if hasattr(inc.income_date,"strftime"):
                                income_date_str = inc.income_date.strftime("%Y-%m-%d")
                            else:
                                income_date_str = str(inc.income_date)
                        except Exception:
                            income_date_str = str(inc.income_date)
                            
                    income_list.append({
                "id": inc.id,
                "source": inc.source,
                "amount": amount,
                "description": description,
                "income_date": income_date_str
            })
            except Exception as inner_e:
                print(f"Error processing expense {inc.id}: {inner_e}")
                continue

        return JSONResponse(status_code=200, content={"status": "success", "data": income_list})

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Server error: {str(e)}"})

@router.post("/income")
async def create_income(income_data: dict, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        source = income_data.get("source", "").strip()
        amount = income_data.get("amount")
        description = income_data.get("description", "").strip()
        income_date = income_data.get("income_date")

        errors = {}
        if not source:
            errors["source"] = "Source is required"
        if not amount or float(amount) <= 0:
            errors["amount"] = "Amount must be > 0"
        if not income_date:
            errors["income_date"] = "Date is required"

        if errors:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Validation failed", "errors": errors})

        new_income = crud_create_income(db, user.id, source, float(amount), description or None, datetime.strptime(income_date, "%Y-%m-%d"))

        return JSONResponse(status_code=201, content={"status": "success", "message": "Income added successfully", "data": {
            "id": new_income.id,
            "source": new_income.source,
            "amount": new_income.amount,
            "description": new_income.description,
            "income_date": new_income.income_date.strftime("%Y-%m-%d")
        }})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error adding income: {str(e)}"})

@router.put("/income/{income_id}")
async def update_income(income_id: int, income_data: dict, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        income = db.query(Income).filter(Income.id == income_id, Income.user_id == user.id).first()
        if not income:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Income not found"})

        source = income_data.get("source", "").strip()
        amount = income_data.get("amount")
        description = income_data.get("description", "").strip()
        income_date = income_data.get("income_date")

        errors = {}
        if not source:
            errors["source"] = "Source is required"
        if not amount or float(amount) <= 0:
            errors["amount"] = "Amount must be > 0"
        if not income_date:
            errors["income_date"] = "Date is required"

        if errors:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Validation failed", "errors": errors})

        updated_income = crud_update_income(db, income_id, user.id, source, float(amount), description or None, datetime.strptime(income_date, "%Y-%m-%d"))
        if not updated_income:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Income not found"})

        return JSONResponse(status_code=200, content={"status": "success", "message": "Income updated successfully", "data": {
            "id": updated_income.id,
            "source": updated_income.source,
            "amount": updated_income.amount,
            "description": updated_income.description,
            "income_date": updated_income.income_date.strftime("%Y-%m-%d")
        }})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error updating income: {str(e)}"})

@router.delete("/income/{income_id}")
async def delete_income(income_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not crud_delete_income(db, income_id, user.id):
            return JSONResponse(status_code=404, content={"status": "error", "message": "Income not found"})

        return JSONResponse(status_code=200, content={"status": "success", "message": "Income deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error deleting income: {str(e)}"})
