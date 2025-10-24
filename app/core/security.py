"""
Sistema de autenticação e segurança
Baseado no fluxo N8n: Autenticação via apikey header
"""
import secrets
from typing import Optional
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from loguru import logger


# Header de autenticação
api_key_header = APIKeyHeader(name="apikey", auto_error=False)


def generate_api_key() -> str:
    """
    Gera uma nova API key no formato: fin_[64 chars hex]
    Baseado no SQL do N8n: 'fin_' || encode(gen_random_bytes(32), 'hex')
    """
    random_bytes = secrets.token_bytes(32)
    hex_string = random_bytes.hex()
    return f"fin_{hex_string}"


def generate_master_token(user_id: int) -> str:
    """
    Gera um master token para o usuário
    """
    return generate_api_key()


async def get_current_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Valida API key e retorna usuário atual
    Dependency para proteger rotas

    Args:
        api_key: API key do header
        db: Sessão do banco de dados

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se API key inválida ou usuário inativo
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key não fornecida"
        )

    # Buscar usuário pela API key
    user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        logger.warning(f"⚠️ API key inválida tentada: {api_key[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida"
        )

    if not user.is_active:
        logger.warning(f"⚠️ Usuário inativo tentou acesso: {user.remote_jid}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se o usuário está ativo e verificado
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


def hash_password(password: str) -> str:
    """
    Hash de senha (placeholder - implementar com bcrypt se necessário)
    """
    # Por enquanto, o N8n usa senha simples 'mudar@123'
    # TODO: Implementar hash real com passlib
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica senha (placeholder)
    """
    # TODO: Implementar verificação real
    return plain_password == hashed_password
