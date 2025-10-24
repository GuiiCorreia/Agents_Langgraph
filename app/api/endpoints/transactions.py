"""
Endpoints de Transações
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse
)
from app.services.transaction_service import transaction_service

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria nova transação

    POST /api/transactions
    Headers: apikey, Accept: application/json
    Body: {
        "descricao": "string",
        "valor": float,
        "tipo": "Receita|Despesa",
        "carteira_id": int,
        "categoria_id": int,
        "data_transacao": "YYYY-MM-DD",
        "status": "Efetivada",
        "forma_pagamento_id": int (optional)
    }
    """
    new_transaction = transaction_service.create(db, current_user, transaction)
    return new_transaction


@router.get("/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca transações recentes do usuário

    GET /api/transactions/recent
    Headers: apikey
    """
    transactions = transaction_service.get_recent(db, current_user, limit)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca transação específica por ID

    GET /api/transactions/{id}
    Headers: apikey
    """
    transaction = transaction_service.get_by_id(db, current_user, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    return transaction


@router.get("/", response_model=List[TransactionResponse])
async def get_all_transactions(
    start_date: Optional[date] = Query(None, alias="data_inicio"),
    end_date: Optional[date] = Query(None, alias="data_fim"),
    category_id: Optional[int] = Query(None, alias="categoria_id"),
    transaction_type: Optional[str] = Query(None, alias="tipo"),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca todas as transações com filtros

    GET /api/transactions?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD&categoria_id=1
    Headers: apikey
    """
    transactions = transaction_service.get_all(
        db,
        current_user,
        start_date,
        end_date,
        category_id,
        transaction_type,
        limit,
        offset
    )
    return transactions


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza transação existente

    PATCH /api/transactions/{id}
    Headers: apikey
    Body: Campos a serem atualizados (todos opcionais)
    """
    updated_transaction = transaction_service.update(
        db,
        current_user,
        transaction_id,
        transaction_update
    )
    if not updated_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta transação

    DELETE /api/transactions/{id}
    Headers: apikey
    """
    success = transaction_service.delete(db, current_user, transaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    return None
