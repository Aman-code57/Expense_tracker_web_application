from sqlalchemy.orm import Session
from models import Income

def get_incomes(db: Session, user_id: int):
    return db.query(Income).filter(Income.user_id == user_id).all()

def create_income(db: Session, user_id: int, source: str, amount: float, description: str, income_date):
    new_income = Income(
        user_id=user_id,
        source=source,
        amount=amount,
        description=description,
        income_date=income_date
    )
    db.add(new_income)
    db.commit()
    db.refresh(new_income)
    return new_income

def update_income(db: Session, income_id: int, user_id: int, source: str, amount: float, description: str, income_date):
    income = db.query(Income).filter(Income.id == income_id, Income.user_id == user_id).first()
    if not income:
        return None
    income.source = source
    income.amount = amount
    income.description = description
    income.income_date = income_date
    db.commit()
    db.refresh(income)
    return income

def delete_income(db: Session, income_id: int, user_id: int):
    income = db.query(Income).filter(Income.id == income_id, Income.user_id == user_id).first()
    if not income:
        return False
    db.delete(income)
    db.commit()
    return True
