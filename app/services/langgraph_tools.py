"""
LangGraph Tools - Ferramentas que o Agent pode usar
Baseado nas tools do N8n: [FLUXO PRINCIPAL] - AI Agent tools
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from loguru import logger

from app.models import User, Category, PaymentMethod, Transaction, Wallet, Reminder
from app.services.transaction_service import transaction_service
from app.schemas.transaction import TransactionCreate
from app.schemas.reminder import ReminderCreate


@tool
def lista_todas_categorias(user_id: int, db: Session) -> str:
    """
    Lista todas as categorias disponíveis para classificar transações.
    Útil quando o usuário quer saber quais categorias existem.

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados

    Returns:
        String formatada com lista de categorias
    """
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()

        if not categories:
            return "Nenhuma categoria encontrada."

        result = "📋 **Categorias Disponíveis:**\n\n"
        for cat in categories:
            icon = cat.icon or "📌"
            tipo = "Receita" if cat.default_type == "income" else "Despesa"
            result += f"{icon} {cat.name} ({tipo})\n"

        return result

    except Exception as e:
        logger.error(f"Erro ao listar categorias: {e}")
        return "Erro ao buscar categorias."


@tool
def busca_informacoes_carteira_atual(user_id: int, db: Session) -> str:
    """
    Busca informações da carteira principal do usuário (saldo atual).

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados

    Returns:
        String formatada com informações da carteira
    """
    try:
        wallet = db.query(Wallet).filter(
            Wallet.user_id == user_id,
            Wallet.is_default == True
        ).first()

        if not wallet:
            wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

        if not wallet:
            return "Nenhuma carteira encontrada."

        saldo_formatado = f"R$ {wallet.current_balance:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return f"""💰 **Carteira: {wallet.name}**

Saldo Atual: {saldo_formatado}
Criada em: {wallet.created_at.strftime('%d/%m/%Y')}"""

    except Exception as e:
        logger.error(f"Erro ao buscar carteira: {e}")
        return "Erro ao buscar informações da carteira."


@tool
def insere_transacao(
    user_id: int,
    db: Session,
    descricao: str,
    valor: float,
    tipo: str,
    data_transacao: str,
    categoria_nome: Optional[str] = None,
    forma_pagamento_nome: Optional[str] = None
) -> str:
    """
    Insere uma nova transação financeira (receita ou despesa).

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        descricao: Descrição da transação
        valor: Valor da transação
        tipo: "receita" ou "despesa"
        data_transacao: Data no formato YYYY-MM-DD ou DD/MM/YYYY
        categoria_nome: Nome da categoria (opcional)
        forma_pagamento_nome: Nome da forma de pagamento (opcional)

    Returns:
        Mensagem de confirmação formatada para WhatsApp
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Erro: Usuário não encontrado."

        # Converter tipo
        transaction_type = "income" if tipo.lower() in ["receita", "renda", "ganho"] else "expense"

        # Parsear data
        try:
            if "/" in data_transacao:
                # Formato DD/MM/YYYY
                parsed_date = datetime.strptime(data_transacao, "%d/%m/%Y").date()
            else:
                # Formato YYYY-MM-DD
                parsed_date = datetime.strptime(data_transacao, "%Y-%m-%d").date()
        except:
            parsed_date = date.today()

        # Buscar categoria por nome
        category_id = None
        if categoria_nome:
            category = db.query(Category).filter(
                Category.name.ilike(f"%{categoria_nome}%")
            ).first()
            if category:
                category_id = category.id

        # Buscar forma de pagamento por nome
        payment_method_id = None
        if forma_pagamento_nome:
            payment_method = db.query(PaymentMethod).filter(
                PaymentMethod.name.ilike(f"%{forma_pagamento_nome}%")
            ).first()
            if payment_method:
                payment_method_id = payment_method.id

        # Criar transação
        transaction_data = TransactionCreate(
            title=descricao,
            description=None,
            amount=abs(valor),
            transaction_type=transaction_type,
            transaction_date=parsed_date,
            category_id=category_id,
            payment_method_id=payment_method_id,
            wallet_id=None,  # Vai usar carteira padrão
            notes=None,
            receipt_url=None,
            tags=None,
            is_recurring=False,
            is_confirmed=True
        )

        transaction = transaction_service.create(db, user, transaction_data)

        # Formatar resposta baseada no template do N8n
        emoji = "🟢" if transaction_type == "income" else "🔴"
        tipo_texto = "RECEITA" if transaction_type == "income" else "DESPESA"
        valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        data_formatada = parsed_date.strftime("%d/%m/%Y")

        categoria_texto = db.query(Category).filter(Category.id == category_id).first().name if category_id else "Sem categoria"
        pagamento_texto = db.query(PaymentMethod).filter(PaymentMethod.id == payment_method_id).first().name if payment_method_id else "Não especificado"

        return f"""{emoji} **{tipo_texto} INSERIDA COM SUCESSO**

*{descricao}*
💰 {valor_formatado}
🗓 {data_formatada}
📊 {categoria_texto}
📍 Forma de pagamento: {pagamento_texto}
🔍 Código: {transaction.id}"""

    except Exception as e:
        logger.error(f"Erro ao inserir transação: {e}")
        return f"Erro ao inserir transação: {str(e)}"


@tool
def transacoes_recentes(user_id: int, db: Session, limite: int = 5) -> str:
    """
    Busca as transações mais recentes do usuário.

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        limite: Número máximo de transações (padrão 5)

    Returns:
        String formatada com lista de transações recentes
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Erro: Usuário não encontrado."

        transactions = transaction_service.get_recent(db, user, limit=limite)

        if not transactions:
            return "Você ainda não tem transações registradas."

        result = f"📊 **Últimas {len(transactions)} Transações:**\n\n"

        for t in transactions:
            emoji = "🟢" if t.transaction_type == "income" else "🔴"
            tipo = "Receita" if t.transaction_type == "income" else "Despesa"
            valor_formatado = f"R$ {t.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data_formatada = t.transaction_date.strftime("%d/%m/%Y")

            categoria = db.query(Category).filter(Category.id == t.category_id).first() if t.category_id else None
            categoria_nome = categoria.name if categoria else "Sem categoria"

            result += f"""{emoji} *{t.title}*
Valor: {valor_formatado} ({tipo})
Data: {data_formatada}
Categoria: {categoria_nome}
ID: {t.id}

"""

        return result

    except Exception as e:
        logger.error(f"Erro ao buscar transações recentes: {e}")
        return "Erro ao buscar transações recentes."


@tool
def resumo_mes_atual(user_id: int, db: Session) -> str:
    """
    Retorna resumo financeiro do mês atual (receitas, despesas, saldo).

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados

    Returns:
        String formatada com resumo do mês
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Erro: Usuário não encontrado."

        # Calcular primeiro e último dia do mês
        today = date.today()
        start_date = date(today.year, today.month, 1)

        if today.month == 12:
            end_date = date(today.year, 12, 31)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

        # Buscar resumo
        summary = transaction_service.get_summary(db, user, start_date, end_date)

        receitas_formatado = f"R$ {summary['total_income']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        despesas_formatado = f"R$ {summary['total_expense']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        saldo_formatado = f"R$ {summary['balance']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        mes_nome = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ][today.month - 1]

        return f"""📊 **Resumo de {mes_nome}/{today.year}**

🟢 Total de Receitas: {receitas_formatado}
🔴 Total de Despesas: {despesas_formatado}
💰 Saldo: {saldo_formatado}
📈 Transações: {summary['transaction_count']}"""

    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return "Erro ao gerar resumo do mês."


@tool
def consulta_forma_pagamento(user_id: int, db: Session) -> str:
    """
    Lista todos os métodos de pagamento disponíveis.

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados

    Returns:
        String formatada com lista de métodos
    """
    try:
        payment_methods = db.query(PaymentMethod).filter(
            PaymentMethod.is_active == True
        ).all()

        if not payment_methods:
            return "Nenhum método de pagamento encontrado."

        result = "💳 **Métodos de Pagamento Disponíveis:**\n\n"
        for pm in payment_methods:
            icon = pm.icon or "💵"
            result += f"{icon} {pm.name}\n"

        return result

    except Exception as e:
        logger.error(f"Erro ao listar métodos de pagamento: {e}")
        return "Erro ao buscar métodos de pagamento."


# Exportar lista de tools para o LangGraph Agent
def get_all_tools(user_id: int, db: Session) -> List:
    """
    Retorna lista de todas as tools disponíveis com contexto do usuário.

    IMPORTANTE: No LangGraph, precisamos usar ferramentas sem estado.
    Vamos criar wrappers que injetam user_id e db automaticamente.
    """
    # TODO: Implementar wrappers que injetam user_id e db
    # Por enquanto, retornamos a lista básica
    return [
        lista_todas_categorias,
        busca_informacoes_carteira_atual,
        insere_transacao,
        transacoes_recentes,
        resumo_mes_atual,
        consulta_forma_pagamento
    ]
