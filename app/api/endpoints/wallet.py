"""
Endpoints de Carteiras e Dashboard
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Wallet
from app.services.transaction_service import transaction_service

router = APIRouter()


@router.get("/current")
async def get_current_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca carteira atual (padrão) do usuário

    GET /api/wallet/current
    Headers: apikey
    Response: {id, nome, saldo_atual, data_criacao}
    """
    wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.is_default == True
    ).first()

    if not wallet:
        # Se não tiver carteira padrão, pegar a primeira
        wallet = db.query(Wallet).filter(
            Wallet.user_id == current_user.id
        ).first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma carteira encontrada"
        )

    return {
        "id": wallet.id,
        "nome": wallet.name,
        "saldo_atual": wallet.current_balance,
        "data_criacao": wallet.created_at
    }


@router.get("/all")
async def get_all_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as carteiras do usuário

    GET /api/wallet/all
    Headers: apikey
    """
    wallets = db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).all()

    return wallets


@router.get("/{wallet_id}")
async def get_wallet(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca carteira específica por ID

    GET /api/wallet/{id}
    Headers: apikey
    """
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )

    return wallet
