from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """
    Schema base para categoria
    """
    name: str = Field(..., description="Nome da categoria")
    description: Optional[str] = Field(None, description="Descrição da categoria")
    default_type: str = Field("expense", description="Tipo padrão: 'expense' ou 'income'")
    icon: Optional[str] = Field(None, description="Ícone/emoji da categoria")
    is_active: bool = Field(True, description="Categoria ativa?")


class CategoryCreate(CategoryBase):
    """
    Schema para criar categoria
    """
    pass


class CategoryUpdate(BaseModel):
    """
    Schema para atualizar categoria
    """
    name: Optional[str] = None
    description: Optional[str] = None
    default_type: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """
    Schema de resposta para categoria
    """
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """
    Schema para lista de categorias
    """
    total: int
    categories: list[CategoryResponse]
