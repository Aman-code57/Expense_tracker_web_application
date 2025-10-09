from sqlalchemy.orm import Session
from models import User

def create_user(db: Session, fullname: str, email: str, gender: str, mobilenumber: str, password: str):
    new_user = User(
        fullname=fullname,
        email=email,
        gender=gender,
        mobilenumber=mobilenumber,
        password=password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_email_or_mobile(db: Session, email: str, mobile: str):
    return db.query(User).filter(
        (User.email == email) | (User.mobilenumber == mobile)
    ).first()

def update_user_reset_token(db: Session, user: User, reset_token: str, expires):
    user.reset_token = reset_token
    user.reset_token_expires = expires
    db.commit()

def update_user_password(db: Session, user: User, new_password: str):
    user.password = new_password
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
