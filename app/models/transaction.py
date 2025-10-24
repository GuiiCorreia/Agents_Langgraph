from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.category import TransactionType


class Transaction(Base):
    """
    Modelo de transação financeira
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)

    # Dados da transação
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'expense' ou 'income'

    # Data da transação
    transaction_date = Column(Date, nullable=False)

    # Metadados
    notes = Column(Text, nullable=True)

    # Arquivo/comprovante (URL ou path)
    receipt_url = Column(String, nullable=True)

    # Tags para facilitar busca
    tags = Column(String, nullable=True)  # JSON ou string separada por vírgulas

    # Status
    is_recurring = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.title} - R$ {self.amount}>"
