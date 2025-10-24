"""
Tools Avançadas - Relatórios e Lembretes
Baseado nos subworkflows do N8n: [RELATORIO DETALHADO] e [INCLUI LEMBRETES]
"""
from typing import Optional
from datetime import datetime, date, timedelta
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from loguru import logger

from app.models import User, Category, Transaction, Reminder
from app.services.transaction_service import transaction_service
from app.integrations.uazapi import uazapi_client
from app.integrations.gemini_client import gemini_client


@tool
def relatorio_detalhado(
    user_id: int,
    db: Session,
    data_inicio: str,
    data_fim: str,
    categoria_nome: Optional[str] = None
) -> str:
    """
    Gera relatório detalhado de transações para um período específico.
    Baseado no subworkflow N8n: [RELATORIO DETALHADO]

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        data_inicio: Data inicial no formato YYYY-MM-DD ou DD/MM/YYYY
        data_fim: Data final no formato YYYY-MM-DD ou DD/MM/YYYY
        categoria_nome: Nome da categoria para filtrar (opcional)

    Returns:
        Relatório formatado com transações do período
    """
    try:
        logger.info(f"📊 Gerando relatório detalhado: {data_inicio} a {data_fim}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Erro: Usuário não encontrado."

        # Parsear datas
        try:
            if "/" in data_inicio:
                start_date = datetime.strptime(data_inicio, "%d/%m/%Y").date()
            else:
                start_date = datetime.strptime(data_inicio, "%Y-%m-%d").date()

            if "/" in data_fim:
                end_date = datetime.strptime(data_fim, "%d/%m/%Y").date()
            else:
                end_date = datetime.strptime(data_fim, "%Y-%m-%d").date()
        except Exception as e:
            return f"Erro ao interpretar datas. Use o formato DD/MM/YYYY ou YYYY-MM-DD. Erro: {e}"

        # Buscar categoria se fornecida
        category_id = None
        if categoria_nome:
            category = db.query(Category).filter(
                Category.name.ilike(f"%{categoria_nome}%")
            ).first()
            if category:
                category_id = category.id
            else:
                return f"Categoria '{categoria_nome}' não encontrada."

        # Buscar transações
        transactions = transaction_service.get_all(
            db,
            user,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )

        if not transactions:
            return f"Nenhuma transação encontrada no período de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}."

        # Separar por tipo
        receitas = [t for t in transactions if t.transaction_type == "income"]
        despesas = [t for t in transactions if t.transaction_type == "expense"]

        total_receitas = sum(t.amount for t in receitas)
        total_despesas = sum(t.amount for t in despesas)
        saldo = total_receitas - total_despesas

        # Formatar relatório
        categoria_texto = f" - Categoria: {categoria_nome}" if categoria_nome else ""

        relatorio = f"""📊 **Relatório Financeiro Detalhado**
Período: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}{categoria_texto}

"""

        # Receitas
        if receitas:
            relatorio += "🟢 **RECEITAS:**\n\n"
            for t in receitas:
                cat = db.query(Category).filter(Category.id == t.category_id).first() if t.category_id else None
                cat_nome = cat.name if cat else "Sem categoria"
                valor_fmt = f"R$ {t.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                relatorio += f"• *{t.title}*\n"
                relatorio += f"  {valor_fmt} | {t.transaction_date.strftime('%d/%m/%Y')} | {cat_nome}\n\n"

        # Despesas
        if despesas:
            relatorio += "🔴 **DESPESAS:**\n\n"
            for t in despesas:
                cat = db.query(Category).filter(Category.id == t.category_id).first() if t.category_id else None
                cat_nome = cat.name if cat else "Sem categoria"
                valor_fmt = f"R$ {t.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                relatorio += f"• *{t.title}*\n"
                relatorio += f"  {valor_fmt} | {t.transaction_date.strftime('%d/%m/%Y')} | {cat_nome}\n\n"

        # Totais
        total_receitas_fmt = f"R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        total_despesas_fmt = f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        saldo_fmt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        relatorio += f"""📈 **RESUMO:**
🟢 Total de Receitas: {total_receitas_fmt}
🔴 Total de Despesas: {total_despesas_fmt}
💰 Saldo do Período: {saldo_fmt}
📊 Total de Transações: {len(transactions)}"""

        return relatorio

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}", exc_info=True)
        return f"Erro ao gerar relatório: {str(e)}"


@tool
async def insere_lembrete(
    user_id: int,
    db: Session,
    titulo: str,
    descricao: str,
    data_lembrete: str
) -> str:
    """
    Cria um novo lembrete e agenda envio via WhatsApp.
    Baseado no subworkflow N8n: [INCLUI LEMBRETES]

    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        titulo: Título do lembrete
        descricao: Descrição detalhada do lembrete
        data_lembrete: Data e hora do lembrete (YYYY-MM-DD HH:MM ou DD/MM/YYYY HH:MM)

    Returns:
        Mensagem de confirmação
    """
    try:
        logger.info(f"🔔 Criando lembrete: {titulo}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Erro: Usuário não encontrado."

        # Parsear data/hora
        try:
            if "/" in data_lembrete:
                # DD/MM/YYYY HH:MM
                reminder_datetime = datetime.strptime(data_lembrete, "%d/%m/%Y %H:%M")
            else:
                # YYYY-MM-DD HH:MM
                reminder_datetime = datetime.strptime(data_lembrete, "%Y-%m-%d %H:%M")
        except:
            try:
                # Tentar apenas data (usar 09:00 como padrão)
                if "/" in data_lembrete:
                    reminder_datetime = datetime.strptime(data_lembrete, "%d/%m/%Y")
                else:
                    reminder_datetime = datetime.strptime(data_lembrete, "%Y-%m-%d")
                reminder_datetime = reminder_datetime.replace(hour=9, minute=0)
            except Exception as e:
                return f"Erro ao interpretar data. Use formato DD/MM/YYYY HH:MM ou YYYY-MM-DD HH:MM. Erro: {e}"

        # Verificar se a data não é no passado
        if reminder_datetime < datetime.now():
            return "Erro: Não é possível criar lembretes para datas passadas."

        # 1. Inserir no banco de dados
        reminder = Reminder(
            user_id=user_id,
            title=titulo,
            description=descricao,
            reminder_date=reminder_datetime,
            is_active=True,
            is_sent=False
        )

        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        # 2. Agendar via Uazapi
        # Converter para timestamp Unix em milissegundos
        timestamp_ms = int(reminder_datetime.timestamp() * 1000)

        # Formatar mensagem para WhatsApp
        whatsapp_message = f"""🔔 **Lembrete**

{descricao}

_Este é um lembrete agendado pelo sistema FinMec_"""

        try:
            await uazapi_client.schedule_message(
                numbers=[user.remote_jid.split("@")[0]],  # Apenas número
                text=whatsapp_message,
                scheduled_timestamp_ms=timestamp_ms,
                delay_min=10,
                delay_max=30,
                info=f"Lembrete ID: {reminder.id}"
            )
        except Exception as e:
            logger.error(f"Erro ao agendar mensagem na Uazapi: {e}")
            # Continuar mesmo se falhar o agendamento na Uazapi

        # Formatar resposta
        data_formatada = reminder_datetime.strftime("%d/%m/%Y às %H:%M")

        return f"""✅ **Lembrete Criado com Sucesso!**

🔔 *{titulo}*
📝 {descricao}
📅 Agendado para: {data_formatada}
🔍 Código: {reminder.id}

Você receberá uma mensagem no WhatsApp na data e hora agendadas."""

    except Exception as e:
        logger.error(f"Erro ao criar lembrete: {e}", exc_info=True)
        return f"Erro ao criar lembrete: {str(e)}"


# Função para obter todas as tools avançadas
def get_advanced_tools():
    """
    Retorna lista de tools avançadas
    """
    return [
        relatorio_detalhado,
        insere_lembrete
    ]
