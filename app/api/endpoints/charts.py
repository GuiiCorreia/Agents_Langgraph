"""
Endpoints de Gráficos
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL]
GET /api/charts/bar e GET /api/charts/pizza
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from collections import defaultdict
import io
import base64

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Transaction, Category
from app.services.transaction_service import transaction_service

router = APIRouter()


@router.get("/bar")
async def get_bar_chart(
    target_date: Optional[date] = Query(None, alias="date"),
    descricao: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera dados para gráfico de barras dos últimos 7 dias

    GET /api/charts/bar?date=YYYY-MM-DD&descricao=optional
    Headers: apikey

    Retorna dados agregados por dia para os últimos 7 dias
    """
    # Se não informado, usar hoje
    if not target_date:
        target_date = date.today()

    # Calcular período (7 dias atrás)
    start_date = target_date - timedelta(days=6)
    end_date = target_date

    # Buscar transações do período
    transactions = transaction_service.get_all(
        db,
        current_user,
        start_date=start_date,
        end_date=end_date
    )

    # Filtrar por descrição se fornecida
    if descricao:
        transactions = [t for t in transactions if descricao.lower() in t.title.lower()]

    # Agrupar por dia
    daily_data = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0})

    for transaction in transactions:
        day_key = transaction.transaction_date.isoformat()
        if transaction.transaction_type == "income":
            daily_data[day_key]["receitas"] += transaction.amount
        else:
            daily_data[day_key]["despesas"] += transaction.amount

    # Garantir que todos os 7 dias estejam no resultado
    result = []
    current_date = start_date
    while current_date <= end_date:
        day_key = current_date.isoformat()
        result.append({
            "data": day_key,
            "receitas": daily_data[day_key]["receitas"],
            "despesas": daily_data[day_key]["despesas"],
            "saldo": daily_data[day_key]["receitas"] - daily_data[day_key]["despesas"]
        })
        current_date += timedelta(days=1)

    return {
        "periodo": {
            "inicio": start_date.isoformat(),
            "fim": end_date.isoformat()
        },
        "dados": result
    }


@router.get("/pizza")
async def get_pizza_chart(
    target_date: Optional[date] = Query(None, alias="date"),
    transaction_type: Optional[str] = Query("expense", alias="tipo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera dados para gráfico de pizza por categoria

    GET /api/charts/pizza?date=YYYY-MM-DD&tipo=expense
    Headers: apikey

    Retorna distribuição por categoria no mês da data fornecida
    """
    # Se não informado, usar hoje
    if not target_date:
        target_date = date.today()

    # Calcular primeiro e último dia do mês
    start_date = date(target_date.year, target_date.month, 1)

    # Último dia do mês
    if target_date.month == 12:
        end_date = date(target_date.year, 12, 31)
    else:
        end_date = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)

    # Buscar transações do período
    transactions = transaction_service.get_all(
        db,
        current_user,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type
    )

    # Agrupar por categoria
    category_data = defaultdict(float)

    for transaction in transactions:
        if transaction.category_id:
            category = db.query(Category).filter(
                Category.id == transaction.category_id
            ).first()
            category_name = category.name if category else "Sem categoria"
        else:
            category_name = "Sem categoria"

        category_data[category_name] += transaction.amount

    # Calcular total e percentuais
    total = sum(category_data.values())

    result = []
    for category_name, amount in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total * 100) if total > 0 else 0
        result.append({
            "categoria": category_name,
            "valor": amount,
            "percentual": round(percentage, 2)
        })

    return {
        "periodo": {
            "inicio": start_date.isoformat(),
            "fim": end_date.isoformat()
        },
        "tipo": transaction_type,
        "total": total,
        "distribuicao": result
    }
