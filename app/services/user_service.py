"""
Serviço de gerenciamento de usuários
Baseado na lógica do N8n: [FLUXO PRINCIPAL] - PostgreSQL queries
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, Wallet
from app.core.security import generate_api_key, generate_master_token, hash_password
from loguru import logger


class UserService:
    """
    Serviço para operações de usuário
    """

    @staticmethod
    def get_by_remote_jid(db: Session, remote_jid: str) -> Optional[User]:
        """
        Busca usuário pelo WhatsApp ID (remote_jid)
        SQL: SELECT * FROM usuarios WHERE remotejid = $1
        """
        return db.query(User).filter(User.remote_jid == remote_jid).first()

    @staticmethod
    def get_by_api_key(db: Session, api_key: str) -> Optional[User]:
        """
        Busca usuário pela API key
        """
        return db.query(User).filter(User.api_key == api_key).first()

    @staticmethod
    def create_user(
        db: Session,
        remote_jid: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        username: Optional[str] = None,
        password: str = "mudar@123"
    ) -> User:
        """
        Cria novo usuário no sistema
        Baseado no SQL do N8n:
        INSERT INTO usuarios (nome, remotejid, email, telefone, senha, tipo_usuario, ativo)
        VALUES ($1, $2, $3, $4, 'mudar@123', 'normal', false)
        """
        # Criar usuário
        user = User(
            remote_jid=remote_jid,
            name=name or remote_jid.split("@")[0],
            email=email,
            phone=phone or remote_jid.split("@")[0],
            username=username or remote_jid,
            hashed_password=hash_password(password),
            is_active=False,  # Inativo até pagamento
            is_verified=False
        )

        db.add(user)
        db.flush()  # Para obter o ID

        logger.info(f"✅ Usuário criado: {user.remote_jid}")
        return user

    @staticmethod
    def create_master_token(db: Session, user: User) -> str:
        """
        Cria master token para o usuário
        SQL: INSERT INTO api_tokens (usuario_id, token, nome, data_criacao, ativo, master...)
        """
        master_token = generate_api_key()
        user.api_key = master_token
        user.master_token = master_token

        db.add(user)
        db.commit()

        logger.info(f"✅ Master token criado para: {user.remote_jid}")
        return master_token

    @staticmethod
    def create_primary_wallet(db: Session, user: User) -> Wallet:
        """
        Cria carteira principal para o usuário
        SQL: INSERT INTO carteiras (usuario_id, nome, descricao, saldo_atual, data_criacao)
        VALUES ($1, 'Principal', 'Carteira principal criada automaticamente', 0.00, NOW())
        """
        wallet = Wallet(
            user_id=user.id,
            name="Principal",
            description="Carteira principal criada automaticamente",
            current_balance=0.0,
            is_default=True,
            is_active=True
        )

        db.add(wallet)
        db.commit()
        db.refresh(wallet)

        logger.info(f"✅ Carteira principal criada para: {user.remote_jid}")
        return wallet

    @staticmethod
    def get_or_create_user(
        db: Session,
        remote_jid: str
    ) -> tuple[User, bool]:
        """
        Busca usuário ou cria se não existir
        Retorna (user, is_new)

        Baseado na lógica do N8n:
        1. Buscar usuário por remote_jid
        2. Se não existir, criar usuário + token + carteira
        3. Verificar se está ativo
        """
        user = UserService.get_by_remote_jid(db, remote_jid)
        is_new = False

        if not user:
            # Criar novo usuário
            user = UserService.create_user(db, remote_jid)
            is_new = True

            # Criar master token
            UserService.create_master_token(db, user)

            # Criar carteira principal
            UserService.create_primary_wallet(db, user)

            db.refresh(user)

        return user, is_new

    @staticmethod
    def activate_user(
        db: Session,
        user: User,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> User:
        """
        Ativa usuário após pagamento
        """
        user.is_active = True

        if username:
            user.username = username
        if password:
            user.hashed_password = hash_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"✅ Usuário ativado: {user.remote_jid}")
        return user


# Instância global do serviço
user_service = UserService()
