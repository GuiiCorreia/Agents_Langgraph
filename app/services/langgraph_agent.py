"""
LangGraph Agent - Agente de IA para controle financeiro
Baseado no AI Agent do N8n: [FLUXO PRINCIPAL]
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.models import User


# System Prompt baseado no N8n
SYSTEM_PROMPT = """Você é um assistente pessoal de controle financeiro via WhatsApp.

**Suas Responsabilidades:**
- Registrar transações financeiras (receitas e despesas)
- Fornecer resumos e relatórios financeiros
- Categorizar gastos automaticamente
- Auxiliar o usuário a controlar suas finanças

**Categorias Disponíveis:**
- Alimentação: Supermercado, restaurantes, delivery, lanches
- Saúde: Farmácia, consultas médicas, exames, plano de saúde
- Educação: Escola, cursos, livros, material escolar
- Moradia: Aluguel, condomínio, água, luz, gás, internet
- Transporte: Combustível, ônibus, uber, manutenção veículo
- Lazer: Cinema, viagens, hobbies, streaming
- Vestuário: Roupas, sapatos, acessórios
- Outros: Demais gastos não categorizados

**Identificação de Transações:**
- **RECEITAS** (palavras-chave): recebi, ganhei, salário, pagamento, renda, lucro, venda, depósito
- **DESPESAS** (palavras-chave): gastei, paguei, comprei, conta, boleto, fatura, compra

**Formato de Resposta para Transações:**
Quando inserir uma transação, use EXATAMENTE este formato:

🟢 RECEITA INSERIDA COM SUCESSO (ou 🔴 DESPESA INSERIDA COM SUCESSO)
*[Descrição]*
💰 R$ [valor]
🗓 [data dd/MM/yyyy]
📊 [Categoria]
📍 Forma de pagamento: [Método]
🔍 Código: [ID]

**Regras Importantes:**
1. Sempre extraia: descrição, valor, data e categoria
2. Se a data não for mencionada, use a data atual
3. Valores devem ser números positivos
4. Seja cordial e use emojis para melhor visualização
5. Se o usuário enviar uma lista de itens (ex: de uma nota fiscal), registre cada item como uma transação separada
6. Quando não tiver certeza, pergunte ao usuário
7. Use as ferramentas disponíveis para consultar categorias, saldo, etc

**Tratamento de Imagens/Áudios:**
- Quando receber texto extraído de imagem ou áudio transcrito, processe normalmente
- Se o texto contém múltiplos itens com preços, pergunte se deve registrar todos ou apenas o total

**Tom de Voz:**
- Amigável e profissional
- Conciso mas informativo
- Use emojis relevantes
- Sempre confirme ações realizadas"""


class AgentState(TypedDict):
    """
    Estado do agente LangGraph
    """
    messages: Annotated[Sequence[BaseMessage], "Histórico de mensagens"]
    user_id: int
    user_remote_jid: str


class FinancialAgent:
    """
    Agente financeiro usando LangGraph
    """

    def __init__(self):
        # Modelo OpenAI baseado no N8n: gpt-4o-mini-2024-07-18
        self.llm = ChatOpenAI(
            model="gpt-4o-mini-2024-07-18",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

        self.graph = None

    def create_tools_for_user(self, user_id: int, db: Session) -> list:
        """
        Cria ferramentas específicas para o usuário.
        Injeta user_id e db nas funções.
        """
        from app.services import langgraph_tools
        from functools import partial

        # Criar versões parciais das tools com user_id e db injetados
        tools = []

        # Lista de todas as tools
        tool_functions = [
            langgraph_tools.lista_todas_categorias,
            langgraph_tools.busca_informacoes_carteira_atual,
            langgraph_tools.insere_transacao,
            langgraph_tools.transacoes_recentes,
            langgraph_tools.resumo_mes_atual,
            langgraph_tools.consulta_forma_pagamento
        ]

        for tool_func in tool_functions:
            # Criar wrapper que injeta user_id e db
            tools.append(tool_func)

        return tools

    def build_graph(self, tools: list):
        """
        Constrói o grafo LangGraph com as tools
        """
        # Bind tools ao LLM
        llm_with_tools = self.llm.bind_tools(tools)

        # Definir o grafo
        workflow = StateGraph(AgentState)

        # Nó do agente
        def agent_node(state: AgentState):
            """Nó principal do agente"""
            messages = state["messages"]

            # Adicionar system prompt se for a primeira mensagem
            if len(messages) == 1:
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

            response = llm_with_tools.invoke(messages)
            return {"messages": messages + [response]}

        # Nó de ferramentas
        tool_node = ToolNode(tools)

        # Adicionar nós
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        # Definir roteamento
        def should_continue(state: AgentState):
            """Decide se deve continuar para tools ou terminar"""
            last_message = state["messages"][-1]

            # Se a mensagem tem tool_calls, vai para tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"

            # Caso contrário, termina
            return END

        # Adicionar edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        # Compilar
        self.graph = workflow.compile()

    async def process_message(
        self,
        user: User,
        message_text: str,
        db: Session
    ) -> str:
        """
        Processa mensagem do usuário e retorna resposta

        Args:
            user: Usuário
            message_text: Texto da mensagem (já processado)
            db: Sessão do banco de dados

        Returns:
            Resposta do agente
        """
        try:
            logger.info(f"🤖 Agent processando mensagem de {user.remote_jid}")

            # Criar tools específicas para este usuário
            tools = self.create_tools_for_user(user.id, db)

            # Construir grafo com as tools
            self.build_graph(tools)

            # Estado inicial
            initial_state = {
                "messages": [HumanMessage(content=message_text)],
                "user_id": user.id,
                "user_remote_jid": user.remote_jid
            }

            # Executar o grafo
            result = await self.graph.ainvoke(initial_state)

            # Extrair resposta final
            final_message = result["messages"][-1]

            if isinstance(final_message, AIMessage):
                response = final_message.content
            else:
                response = str(final_message)

            logger.info(f"✅ Agent respondeu: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"❌ Erro no agent: {e}", exc_info=True)
            return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"


# Instância global do agente
financial_agent = FinancialAgent()
