from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class TransactionBase(BaseModel):
    """
    Schema base para transação
    """
    title: str = Field(..., description="Título da transação")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    amount: float = Field(..., gt=0, description="Valor da transação")
    transaction_type: str = Field(..., description="Tipo: 'expense' ou 'income'")
    transaction_date: date = Field(..., description="Data da transação")
    category_id: Optional[int] = Field(None, description="ID da categoria")
    payment_method_id: Optional[int] = Field(None, description="ID do método de pagamento")
    wallet_id: Optional[int] = Field(None, description="ID da carteira")
    notes: Optional[str] = Field(None, description="Notas adicionais")
    receipt_url: Optional[str] = Field(None, description="URL do comprovante")
    tags: Optional[str] = Field(None, description="Tags separadas por vírgula")
    is_recurring: bool = Field(False, description="É transação recorrente?")
    is_confirmed: bool = Field(True, description="Está confirmada?")


class TransactionCreate(TransactionBase):
    """
    Schema para criar transação
    """
    pass


class TransactionUpdate(BaseModel):
    """
    Schema para atualizar transação (todos campos opcionais)
    """
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    wallet_id: Optional[int] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    tags: Optional[str] = None
    is_recurring: Optional[bool] = None
    is_confirmed: Optional[bool] = None


class TransactionResponse(TransactionBase):
    """
    Schema de resposta para transação
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """
    Schema para lista de transações
    """
    total: int
    transactions: list[TransactionResponse]
