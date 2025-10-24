from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    """
    Modelo de usuário do sistema
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    remote_jid = Column(String, unique=True, index=True, nullable=False)  # WhatsApp ID
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)

    # Credenciais de acesso web
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)

    # Tokens de autenticação
    api_key = Column(String, unique=True, nullable=True, index=True)
    master_token = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Domínio personalizado (se houver)
    domain = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.remote_jid}>"
