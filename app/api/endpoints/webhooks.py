"""
Webhooks - Recebe mensagens do WhatsApp
Baseado no N8n: [FLUXO PRINCIPAL] - Webhook /finmec
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger

from app.db.database import get_db
from app.schemas.webhook import WebhookRequest
from app.schemas.user import UserActivationRequest
from app.services.user_service import user_service
from app.services.message_processor import message_processor
from app.services.langgraph_agent import financial_agent
from app.integrations.uazapi import uazapi_client

router = APIRouter()


@router.post("/finmec")
async def webhook_whatsapp(
    webhook_data: WebhookRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook principal que recebe mensagens do WhatsApp via Uazapi

    POST /webhook/finmec
    Body: {
        "remoteJid": "556492517702@s.whatsapp.net",
        "instanceId": "finmec",
        "message": {
            "type": "conversation|audiomessage|imagemessage|documentmessage",
            "body": "texto da mensagem",
            ...
        }
    }

    Fluxo:
    1. Validar webhook
    2. Buscar ou criar usuário
    3. Verificar se está ativo
    4. Processar mensagem baseado no tipo
    5. Enviar para LangGraph Agent
    6. Responder no WhatsApp
    """
    try:
        remote_jid = webhook_data.remoteJid
        message = webhook_data.message
        message_type = message.type
        message_id = message.id

        logger.info(f"📩 Webhook recebido de {remote_jid} - Tipo: {message_type}")

        # 1. Buscar ou criar usuário
        user, is_new = user_service.get_or_create_user(db, remote_jid)

        # 2. Verificar se usuário está ativo
        if not user.is_active:
            # Usuário inativo (não pagou)
            logger.warning(f"⚠️ Usuário inativo tentou usar o sistema: {remote_jid}")

            inactive_message = """👋 Olá! Obrigado por entrar em contato.

Para usar o sistema de controle financeiro, você precisa ativar sua conta primeiro.

Entre em contato conosco para mais informações sobre como ativar."""

            # Enviar mensagem de forma assíncrona
            background_tasks.add_task(
                uazapi_client.send_text,
                remote_jid,
                inactive_message
            )

            return {"status": "user_inactive", "message": "Usuário inativo"}

        # 3. Processar mensagem baseado no tipo
        try:
            processed_text = await message_processor.route_and_process(
                message_type=message_type,
                message_data=message.dict(),
                message_id=message_id
            )
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            processed_text = "Desculpe, tive um problema ao processar sua mensagem."

        logger.info(f"📝 Texto processado: {processed_text[:100]}...")

        # 4. Enviar para LangGraph Agent
        try:
            agent_response = await financial_agent.process_message(
                user=user,
                message_text=processed_text,
                db=db
            )
        except Exception as e:
            logger.error(f"❌ Erro no agent: {e}", exc_info=True)
            agent_response = "Desculpe, tive um problema ao processar sua solicitação. Tente novamente em alguns instantes."

        logger.info(f"🤖 Agent respondeu: {agent_response[:100]}...")

        # 5. Responder no WhatsApp (em background para não bloquear)
        background_tasks.add_task(
            uazapi_client.send_text,
            remote_jid,
            agent_response
        )

        return {
            "status": "success",
            "message": "Mensagem processada com sucesso",
            "user_id": user.id,
            "processed": True
        }

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar webhook: {str(e)}"
        )


@router.post("/ativacao")
async def webhook_user_activation(
    activation_data: UserActivationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook de ativação de usuário
    Baseado no N8n: [ATIVACAO USUARIO]

    POST /webhook/ativacao
    Body: {
        "telefone": "556281798421",
        "dominio": "https://finmec.gcdutra.cloud",
        "mensagem_ativacao": {
            "titulo": "Sua conta foi ativada!",
            "mensagem": "Olá! Temos uma ótima notícia..."
        },
        "acesso_web": {
            "usuario": "556281798421@s.whatsapp.net",
            "senha": "x6MH9p0M"
        }
    }

    Fluxo:
    1. Buscar usuário por telefone
    2. Ativar usuário
    3. Enviar mensagem de boas-vindas com credenciais via WhatsApp
    """
    try:
        telefone = activation_data.telefone
        dominio = activation_data.dominio or "https://finmec-hom.gcdutra.cloud"
        mensagem_ativacao = activation_data.mensagem_ativacao
        acesso_web = activation_data.acesso_web

        logger.info(f"🎉 Ativação de usuário: {telefone}")

        # Construir remote_jid
        remote_jid = f"{telefone}@s.whatsapp.net" if "@" not in telefone else telefone

        # 1. Buscar usuário
        user = user_service.get_by_remote_jid(db, remote_jid)

        if not user:
            # Criar usuário se não existir
            user, _ = user_service.get_or_create_user(db, remote_jid)

        # 2. Ativar usuário
        user = user_service.activate_user(
            db,
            user,
            username=acesso_web.get("usuario"),
            password=acesso_web.get("senha")
        )

        # 3. Montar mensagem de ativação
        welcome_message = f"""{mensagem_ativacao or 'Sua conta foi ativada com sucesso!'}

Segue abaixo as credenciais de acesso 👇🏼

Acesse a plataforma pelo link abaixo:
{dominio}

*Usuario*: {acesso_web.get('usuario')}
*Senha*: {acesso_web.get('senha')}

Acesse o sistema e faça a troca do seu E-mail e Senha.

Agora você pode começar a usar o sistema de controle financeiro via WhatsApp! 🎉

Digite *ajuda* para ver os comandos disponíveis."""

        # 4. Enviar mensagem via WhatsApp (em background)
        background_tasks.add_task(
            uazapi_client.send_text,
            telefone,
            welcome_message,
            read_chat=True,
            link_preview=True
        )

        logger.info(f"✅ Usuário ativado e mensagem enviada: {telefone}")

        return {
            "status": "success",
            "message": "Usuário ativado com sucesso",
            "user_id": user.id,
            "remote_jid": user.remote_jid
        }

    except Exception as e:
        logger.error(f"❌ Erro na ativação: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao ativar usuário: {str(e)}"
        )


@router.get("/test")
async def test_webhook():
    """
    Endpoint de teste para verificar se o webhook está funcionando
    """
    return {
        "status": "ok",
        "message": "Webhook está funcionando!",
        "endpoints": [
            "/webhook/finmec - Recebe mensagens do WhatsApp",
            "/webhook/ativacao - Ativa usuários"
        ]
    }
