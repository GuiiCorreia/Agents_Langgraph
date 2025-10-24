from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class PaymentMethod(Base):
    """
    Modelo de método de pagamento
    Ex: Dinheiro, Cartão de Crédito, Cartão de Débito, PIX, etc.
    """
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Ícone/emoji para o método
    icon = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Métodos do sistema não podem ser deletados

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    transactions = relationship("Transaction", back_populates="payment_method")

    def __repr__(self):
        return f"<PaymentMethod {self.name}>"
