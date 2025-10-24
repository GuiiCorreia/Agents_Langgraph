from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Schema base para usuário
    """
    remote_jid: str = Field(..., description="WhatsApp ID do usuário")
    name: Optional[str] = Field(None, description="Nome do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    phone: Optional[str] = Field(None, description="Telefone do usuário")


class UserCreate(UserBase):
    """
    Schema para criar usuário
    """
    username: Optional[str] = None
    password: Optional[str] = None
    domain: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Schema para atualizar usuário
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    """
    Schema de resposta para usuário
    """
    id: int
    remote_jid: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    is_verified: bool
    domain: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserActivationRequest(BaseModel):
    """
    Schema para ativação de usuário (webhook)
    """
    telefone: str = Field(..., description="Telefone do usuário")
    dominio: Optional[str] = Field(None, description="Domínio personalizado")
    mensagem_ativacao: Optional[str] = Field(None, description="Mensagem de boas-vindas")
    acesso_web: dict = Field(..., description="Credenciais de acesso web")

    class Config:
        json_schema_extra = {
            "example": {
                "telefone": "5511999999999",
                "dominio": "https://finmec.com.br",
                "mensagem_ativacao": "Bem-vindo ao FinMec!",
                "acesso_web": {
                    "usuario": "usuario123",
                    "senha": "senha123"
                }
            }
        }
