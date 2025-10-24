"""
Endpoints de Categorias
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Category
from app.schemas.category import CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as categorias disponíveis

    GET /api/categories
    Headers: apikey
    Response: Array de {id, nome, descricao, usuario_id}
    """
    categories = db.query(Category).filter(Category.is_active == True).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca categoria específica por ID

    GET /api/categories/{id}
    Headers: apikey
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return category
