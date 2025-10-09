from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    income_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="incomes")

    def __repr__(self):
        return f"<Income(id={self.id}, source={self.source}, amount={self.amount})>"