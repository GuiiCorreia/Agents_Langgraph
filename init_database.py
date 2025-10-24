"""
Script para inicializar o banco de dados
Execute: python init_database.py
"""
import sys
sys.path.insert(0, ".")

from app.db.init_db import init_db, create_default_categories, create_default_payment_methods
from app.db.database import SessionLocal
from loguru import logger


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 INICIALIZANDO BANCO DE DADOS - FinMec")
    logger.info("=" * 60)

    try:
        # 1. Criar tabelas
        logger.info("\n📊 Passo 1: Criando tabelas no banco de dados...")
        init_db()

        # 2. Criar dados padrão
        logger.info("\n📋 Passo 2: Inserindo categorias padrão...")
        db = SessionLocal()
        try:
            create_default_categories(db)

            logger.info("\n💳 Passo 3: Inserindo métodos de pagamento padrão...")
            create_default_payment_methods(db)

            logger.info("\n" + "=" * 60)
            logger.info("✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
            logger.info("=" * 60)

            logger.info("\n📊 Resumo:")
            logger.info("  ✓ Tabelas criadas")
            logger.info("  ✓ Categorias inseridas")
            logger.info("  ✓ Métodos de pagamento inseridos")

            logger.info("\n🚀 Próximo passo: Execute 'python run.py' para iniciar o servidor")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"\n❌ ERRO ao inicializar banco de dados: {e}")
        logger.error("Verifique as credenciais do PostgreSQL no arquivo .env")
        sys.exit(1)
