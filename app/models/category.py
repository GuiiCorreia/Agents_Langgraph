from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class TransactionType(str, enum.Enum):
    """
    Tipos de transação
    """
    EXPENSE = "expense"  # Despesa
    INCOME = "income"    # Receita


class Category(Base):
    """
    Modelo de categoria de transações
    Baseado nas categorias do N8n: Alimentação, Saúde, Educação,
    Moradia, Transporte, Lazer, Vestuário, Outros
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Tipo padrão da categoria (expense ou income)
    default_type = Column(Enum(TransactionType), default=TransactionType.EXPENSE)

    # Ícone/emoji para a categoria
    icon = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Categorias do sistema não podem ser deletadas

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"
