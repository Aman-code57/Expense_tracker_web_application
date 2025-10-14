from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User,Expense
from core.security import verify_token
from crud.expense_crud import get_expenses as crud_get_expenses, create_expense as crud_create_expense, update_expense as crud_update_expense, delete_expense as crud_delete_expense

router = APIRouter()

@router.get("/expense")
async def get_expenses_safe(email: str = Depends(verify_token), db: Session = Depends(get_db)):
   
    try:
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

      
        expense_records = crud_get_expenses(db, user.id)
        expense_list = []

        for exp in expense_records:
            try:
                
                amount = float(exp.amount) if exp.amount else 0.0

               
                category = exp.category or ""
                description = exp.description or ""

            
                date_str = ""
                if exp.date:
                    try:
                        if hasattr(exp.date, "strftime"):
                            date_str = exp.date.strftime("%Y-%m-%d")
                        else:
                            date_str = str(exp.date)
                    except Exception:
                        date_str = str(exp.date)

                expense_list.append({
                    "id": exp.id,
                    "amount": amount,
                    "category": category,
                    "description": description,
                    "date": date_str
                })
            except Exception as inner_e:
                print(f"Error processing expense {exp.id}: {inner_e}")
                continue

        return JSONResponse(status_code=200, content={"status": "success", "data": expense_list})

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Server error: {str(e)}"})


@router.post("/expense")
async def create_expense(expense_data: dict, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        amount = expense_data.get("amount")
        category = expense_data.get("category", "").strip()
        description = expense_data.get("description", "").strip()
        date = expense_data.get("date")

        errors = {}
        if not amount or float(amount) <= 0:
            errors["amount"] = "Amount must be > 0"
        if not category:
            errors["category"] = "Category is required"
        if not date:
            errors["date"] = "Date is required"

        if errors:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Validation failed", "errors": errors})

        new_expense = crud_create_expense(db, user.id, float(amount), category, description or None, datetime.strptime(date, "%Y-%m-%d"))

        return JSONResponse(status_code=201, content={"status": "success", "message": "Expense added successfully", "data": {
            "id": new_expense.id,
            "amount": float(new_expense.amount) if new_expense.amount is not None else 0.0,
            "category": new_expense.category,
            "description": new_expense.description,
            "date": new_expense.date.strftime("%Y-%m-%d") if new_expense.date and hasattr(new_expense.date, 'strftime') else ""
        }})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error adding expense: {str(e)}"})

@router.put("/expense/{expense_id}")
async def update_expense(expense_id: int, expense_data: dict, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
        if not expense:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Expense not found"})

        amount = expense_data.get("amount")
        category = expense_data.get("category", "").strip()
        description = expense_data.get("description", "").strip()
        date = expense_data.get("date")

        errors = {}
        if not amount or float(amount) <= 0:
            errors["amount"] = "Amount must be > 0"
        if not category:
            errors["category"] = "Category is required"
        if not date:
            errors["date"] = "Date is required"

        if errors:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Validation failed", "errors": errors})

        updated_expense = crud_update_expense(db, expense_id, user.id, float(amount), category, description or None, datetime.strptime(date, "%Y-%m-%d"))
        if not updated_expense:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Expense not found"})

        return JSONResponse(status_code=200, content={"status": "success", "message": "Expense updated successfully", "data": {
            "id": updated_expense.id,
            "amount": float(updated_expense.amount) if updated_expense.amount is not None else 0.0,
            "category": updated_expense.category,
            "description": updated_expense.description,
            "date": updated_expense.date.strftime("%Y-%m-%d") if updated_expense.date and hasattr(updated_expense.date, 'strftime') else ""
        }})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error updating expense: {str(e)}"})

@router.delete("/expense/{expense_id}")
async def delete_expense(expense_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not crud_delete_expense(db, expense_id, user.id):
            return JSONResponse(status_code=404, content={"status": "error", "message": "Expense not found"})

        return JSONResponse(status_code=200, content={"status": "success", "message": "Expense deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error deleting expense: {str(e)}"})
