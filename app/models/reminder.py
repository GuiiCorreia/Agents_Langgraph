from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Reminder(Base):
    """
    Modelo de lembrete de pagamento/transação
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamento
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Dados do lembrete
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Data e hora do lembrete
    reminder_date = Column(DateTime(timezone=True), nullable=False)

    # Status
    is_sent = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Data em que foi enviado (se já foi)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Metadados adicionais
    extra_data = Column(Text, nullable=True)  # JSON string com dados extras

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder {self.title} - {self.reminder_date}>"
