from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReminderBase(BaseModel):
    """
    Schema base para lembrete
    """
    title: str = Field(..., description="Título do lembrete")
    description: Optional[str] = Field(None, description="Descrição do lembrete")
    reminder_date: datetime = Field(..., description="Data e hora do lembrete")
    is_active: bool = Field(True, description="Lembrete ativo?")
    extra_data: Optional[str] = Field(None, description="Dados adicionais em JSON")


class ReminderCreate(ReminderBase):
    """
    Schema para criar lembrete
    """
    pass


class ReminderUpdate(BaseModel):
    """
    Schema para atualizar lembrete
    """
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    extra_data: Optional[str] = None


class ReminderResponse(ReminderBase):
    """
    Schema de resposta para lembrete
    """
    id: int
    user_id: int
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """
    Schema para lista de lembretes
    """
    total: int
    reminders: list[ReminderResponse]
