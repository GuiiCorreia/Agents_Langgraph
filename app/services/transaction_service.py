"""
Serviço de gerenciamento de transações
Baseado na lógica do N8n: [FLUXO PRINCIPAL] - Transaction operations
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models import Transaction, User, Category, PaymentMethod, Wallet
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from loguru import logger


class TransactionService:
    """
    Serviço para operações de transações
    """

    @staticmethod
    def create(
        db: Session,
        user: User,
        transaction_data: TransactionCreate
    ) -> Transaction:
        """
        Cria nova transação
        POST /api/transactions
        """
        # Buscar carteira padrão do usuário se não especificada
        wallet_id = transaction_data.wallet_id
        if not wallet_id:
            default_wallet = db.query(Wallet).filter(
                Wallet.user_id == user.id,
                Wallet.is_default == True
            ).first()
            wallet_id = default_wallet.id if default_wallet else None

        transaction = Transaction(
            user_id=user.id,
            title=transaction_data.title,
            description=transaction_data.description,
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            category_id=transaction_data.category_id,
            payment_method_id=transaction_data.payment_method_id,
            wallet_id=wallet_id,
            notes=transaction_data.notes,
            receipt_url=transaction_data.receipt_url,
            tags=transaction_data.tags,
            is_recurring=transaction_data.is_recurring,
            is_confirmed=transaction_data.is_confirmed
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Atualizar saldo da carteira
        if wallet_id:
            TransactionService._update_wallet_balance(db, wallet_id)

        logger.info(f"✅ Transação criada: {transaction.title} - R$ {transaction.amount}")
        return transaction

    @staticmethod
    def get_by_id(db: Session, user: User, transaction_id: int) -> Optional[Transaction]:
        """
        Busca transação específica por ID
        GET /api/transactions/{id}
        """
        return db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()

    @staticmethod
    def get_recent(
        db: Session,
        user: User,
        limit: int = 10
    ) -> List[Transaction]:
        """
        Busca transações recentes do usuário
        GET /api/transactions/recent
        """
        return db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(
            Transaction.transaction_date.desc(),
            Transaction.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_all(
        db: Session,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Transaction]:
        """
        Busca todas as transações com filtros
        GET /api/transactions
        """
        query = db.query(Transaction).filter(Transaction.user_id == user.id)

        # Filtros
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        # Ordenação e paginação
        query = query.order_by(Transaction.transaction_date.desc())

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()

    @staticmethod
    def update(
        db: Session,
        user: User,
        transaction_id: int,
        transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """
        Atualiza transação existente
        PATCH /api/transactions/{id}
        """
        transaction = TransactionService.get_by_id(db, user, transaction_id)
        if not transaction:
            return None

        # Atualizar apenas campos fornecidos
        update_data = transaction_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Atualizar saldo da carteira
        if transaction.wallet_id:
            TransactionService._update_wallet_balance(db, transaction.wallet_id)

        logger.info(f"✅ Transação atualizada: {transaction.id}")
        return transaction

    @staticmethod
    def delete(db: Session, user: User, transaction_id: int) -> bool:
        """
        Deleta transação
        DELETE /api/transactions/{id}
        """
        transaction = TransactionService.get_by_id(db, user, transaction_id)
        if not transaction:
            return False

        wallet_id = transaction.wallet_id

        db.delete(transaction)
        db.commit()

        # Atualizar saldo da carteira
        if wallet_id:
            TransactionService._update_wallet_balance(db, wallet_id)

        logger.info(f"✅ Transação deletada: {transaction_id}")
        return True

    @staticmethod
    def get_summary(
        db: Session,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Retorna resumo de transações (receitas, despesas, saldo)
        Usado em /api/dashboard/summary
        """
        query = db.query(Transaction).filter(Transaction.user_id == user.id)

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        transactions = query.all()

        total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
        total_expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
        balance = total_income - total_expense

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(transactions)
        }

    @staticmethod
    def _update_wallet_balance(db: Session, wallet_id: int):
        """
        Recalcula e atualiza o saldo da carteira
        """
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            return

        # Somar todas as transações da carteira
        transactions = db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id
        ).all()

        balance = 0.0
        for t in transactions:
            if t.transaction_type == "income":
                balance += t.amount
            else:
                balance -= t.amount

        wallet.current_balance = balance
        db.add(wallet)
        db.commit()

        logger.info(f"✅ Saldo da carteira {wallet_id} atualizado: R$ {balance}")


# Instância global
transaction_service = TransactionService()
