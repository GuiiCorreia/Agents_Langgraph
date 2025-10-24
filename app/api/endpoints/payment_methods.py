"""
Endpoints de Métodos de Pagamento
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, PaymentMethod
from app.schemas.payment_method import PaymentMethodResponse

router = APIRouter()


@router.get("/", response_model=List[PaymentMethodResponse])
async def get_all_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os métodos de pagamento disponíveis

    GET /api/payment-methods
    Headers: apikey
    """
    payment_methods = db.query(PaymentMethod).filter(
        PaymentMethod.is_active == True
    ).all()
    return payment_methods


@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    payment_method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca método de pagamento específico por ID

    GET /api/payment-methods/{id}
    Headers: apikey
    """
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado"
        )
    return payment_method
