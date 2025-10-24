"""
Endpoints de Dashboard
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.transaction_service import transaction_service

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    start_date: Optional[date] = Query(None, alias="data_inicio"),
    end_date: Optional[date] = Query(None, alias="data_fim"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna resumo do dashboard financeiro

    GET /api/dashboard/summary
    Headers: apikey
    Query params: data_inicio, data_fim (opcionais)

    Se não informado, usa o mês atual
    """
    # Se não informado, usar mês atual
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)

    if not end_date:
        today = date.today()
        # Último dia do mês
        if today.month == 12:
            end_date = date(today.year, 12, 31)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Buscar resumo
    summary = transaction_service.get_summary(
        db,
        current_user,
        start_date,
        end_date
    )

    return {
        "periodo": {
            "data_inicio": start_date.isoformat(),
            "data_fim": end_date.isoformat()
        },
        "total_receitas": summary["total_income"],
        "total_despesas": summary["total_expense"],
        "saldo": summary["balance"],
        "quantidade_transacoes": summary["transaction_count"]
    }
