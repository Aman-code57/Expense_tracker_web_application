from sqlalchemy.orm import Session
from models import Expense

def get_expenses(db: Session, user_id: int):
    return db.query(Expense).filter(Expense.user_id == user_id).all()

def create_expense(db: Session, user_id: int, amount: float, category: str, description: str, date):
    new_expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category,
        description=description,
        date=date
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

def update_expense(db: Session, expense_id: int, user_id: int, amount: float, category: str, description: str, date):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
    if not expense:
        return None
    expense.amount = amount
    expense.category = category
    expense.description = description
    expense.date = date
    db.commit()
    db.refresh(expense)
    return expense

def delete_expense(db: Session, expense_id: int, user_id: int):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
    if not expense:
        return False
    db.delete(expense)
    db.commit()
    return True
