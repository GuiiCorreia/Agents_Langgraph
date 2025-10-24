from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentMethodBase(BaseModel):
    """
    Schema base para método de pagamento
    """
    name: str = Field(..., description="Nome do método de pagamento")
    description: Optional[str] = Field(None, description="Descrição do método")
    icon: Optional[str] = Field(None, description="Ícone/emoji do método")
    is_active: bool = Field(True, description="Método ativo?")


class PaymentMethodCreate(PaymentMethodBase):
    """
    Schema para criar método de pagamento
    """
    pass


class PaymentMethodUpdate(BaseModel):
    """
    Schema para atualizar método de pagamento
    """
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    """
    Schema de resposta para método de pagamento
    """
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentMethodListResponse(BaseModel):
    """
    Schema para lista de métodos de pagamento
    """
    total: int
    payment_methods: list[PaymentMethodResponse]
