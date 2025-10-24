"""
Script para inicializar o banco de dados
"""
from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.models import Category, PaymentMethod, TransactionType
from loguru import logger


def init_db():
    """
    Cria todas as tabelas no banco de dados
    """
    logger.info("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tabelas criadas com sucesso!")


def create_default_categories(db: Session):
    """
    Cria categorias padrão baseadas no fluxo N8n
    """
    default_categories = [
        {"name": "Alimentação", "icon": "🍽️", "default_type": TransactionType.EXPENSE},
        {"name": "Saúde", "icon": "🏥", "default_type": TransactionType.EXPENSE},
        {"name": "Educação", "icon": "📚", "default_type": TransactionType.EXPENSE},
        {"name": "Moradia", "icon": "🏠", "default_type": TransactionType.EXPENSE},
        {"name": "Transporte", "icon": "🚗", "default_type": TransactionType.EXPENSE},
        {"name": "Lazer", "icon": "🎮", "default_type": TransactionType.EXPENSE},
        {"name": "Vestuário", "icon": "👔", "default_type": TransactionType.EXPENSE},
        {"name": "Outros", "icon": "📦", "default_type": TransactionType.EXPENSE},
        {"name": "Salário", "icon": "💰", "default_type": TransactionType.INCOME},
        {"name": "Investimentos", "icon": "📈", "default_type": TransactionType.INCOME},
        {"name": "Freelance", "icon": "💻", "default_type": TransactionType.INCOME},
    ]

    for cat_data in default_categories:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(
                name=cat_data["name"],
                icon=cat_data["icon"],
                default_type=cat_data["default_type"],
                is_system=True
            )
            db.add(category)
            logger.info(f"✅ Categoria criada: {cat_data['name']}")

    db.commit()
    logger.info("✅ Categorias padrão criadas!")


def create_default_payment_methods(db: Session):
    """
    Cria métodos de pagamento padrão
    """
    default_methods = [
        {"name": "Dinheiro", "icon": "💵"},
        {"name": "Cartão de Crédito", "icon": "💳"},
        {"name": "Cartão de Débito", "icon": "💳"},
        {"name": "PIX", "icon": "📱"},
        {"name": "Transferência Bancária", "icon": "🏦"},
        {"name": "Boleto", "icon": "📄"},
    ]

    for method_data in default_methods:
        existing = db.query(PaymentMethod).filter(PaymentMethod.name == method_data["name"]).first()
        if not existing:
            method = PaymentMethod(
                name=method_data["name"],
                icon=method_data["icon"],
                is_system=True
            )
            db.add(method)
            logger.info(f"✅ Método de pagamento criado: {method_data['name']}")

    db.commit()
    logger.info("✅ Métodos de pagamento padrão criados!")


if __name__ == "__main__":
    from app.db.database import SessionLocal

    logger.info("🚀 Inicializando banco de dados...")

    # Criar tabelas
    init_db()

    # Criar dados padrão
    db = SessionLocal()
    try:
        create_default_categories(db)
        create_default_payment_methods(db)
        logger.info("✅ Banco de dados inicializado com sucesso!")
    finally:
        db.close()
