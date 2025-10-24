"""
Processadores de mensagens do WhatsApp
Baseado no fluxo N8n: [FLUXO PRINCIPAL] - Message routing logic
"""
import base64
from typing import Dict, Any, Optional
from loguru import logger

from app.integrations.uazapi import uazapi_client
from app.integrations.openai_client import openai_client
from app.integrations.gemini_client import gemini_client


class MessageProcessor:
    """
    Processa diferentes tipos de mensagens recebidas do WhatsApp
    """

    @staticmethod
    async def process_conversation(message_data: Dict[str, Any]) -> str:
        """
        Processa mensagem de texto simples (Conversation)

        Args:
            message_data: Dados da mensagem do webhook

        Returns:
            Texto da mensagem
        """
        # Extrair texto da mensagem
        text = message_data.get("conversation") or message_data.get("body") or ""

        logger.info(f"📝 Mensagem de texto recebida: {text[:100]}...")
        return text

    @staticmethod
    async def process_extended_text(message_data: Dict[str, Any]) -> str:
        """
        Processa mensagem de texto estendida (ExtendedTextMessage)

        Args:
            message_data: Dados da mensagem do webhook

        Returns:
            Texto da mensagem
        """
        text = message_data.get("body") or message_data.get("conversation") or ""

        logger.info(f"📝 Mensagem de texto estendida recebida: {text[:100]}...")
        return text

    @staticmethod
    async def process_audio(message_data: Dict[str, Any], message_id: str) -> str:
        """
        Processa mensagem de áudio (AudioMessage)

        Fluxo:
        1. Baixar áudio via Uazapi (base64)
        2. Transcrever com OpenAI Whisper
        3. Retornar transcrição

        Args:
            message_data: Dados da mensagem do webhook
            message_id: ID da mensagem para download

        Returns:
            Texto transcrito do áudio
        """
        try:
            logger.info(f"🎤 Processando mensagem de áudio: {message_id}")

            # 1. Baixar áudio via Uazapi
            media_data = await uazapi_client.download_media(
                message_id=message_id,
                return_base64=True
            )

            audio_base64 = media_data.get("base64Data")
            mimetype = media_data.get("mimetype", "audio/mpeg")

            if not audio_base64:
                logger.error("❌ Áudio não retornou base64")
                return "Não consegui processar o áudio. Tente enviar novamente."

            # 2. Transcrever com OpenAI Whisper
            # Determinar extensão baseada no mimetype
            extension_map = {
                "audio/mpeg": "mp3",
                "audio/ogg": "ogg",
                "audio/wav": "wav",
                "audio/mp4": "m4a"
            }
            extension = extension_map.get(mimetype, "mp3")
            filename = f"audio.{extension}"

            transcription = await openai_client.transcribe_audio(
                audio_base64=audio_base64,
                filename=filename,
                language="pt"
            )

            logger.info(f"✅ Áudio transcrito com sucesso: {transcription[:100]}...")
            return transcription

        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {e}")
            return "Desculpe, tive um problema ao processar seu áudio. Pode tentar enviar novamente ou escrever a mensagem?"

    @staticmethod
    async def process_image(message_data: Dict[str, Any], message_id: str) -> str:
        """
        Processa mensagem de imagem (ImageMessage)

        Fluxo:
        1. Baixar imagem via Uazapi (base64)
        2. Analisar com Google Gemini Vision
        3. Retornar itens e preços extraídos

        Args:
            message_data: Dados da mensagem do webhook
            message_id: ID da mensagem para download

        Returns:
            Texto com itens e preços extraídos da imagem
        """
        try:
            logger.info(f"🖼️ Processando mensagem de imagem: {message_id}")

            # 1. Baixar imagem via Uazapi
            media_data = await uazapi_client.download_media(
                message_id=message_id,
                return_base64=True
            )

            image_base64 = media_data.get("base64Data")
            mimetype = media_data.get("mimetype", "image/jpeg")

            if not image_base64:
                logger.error("❌ Imagem não retornou base64")
                return "Não consegui processar a imagem. Tente enviar novamente."

            # 2. Analisar com Gemini Vision
            # Prompt customizado para extrair itens e preços
            prompt = """Descreva todos os itens presentes nessa imagem que tenham um preço associado.
Para cada item identificado, formate a saída da seguinte maneira:

Comprei [nome do item] por [valor do item].

Regras importantes:
1. Use APENAS números para os valores (sem símbolos de moeda)
2. Coloque cada item em uma nova linha
3. Se não houver itens com preço, responda: "Não encontrei itens com preço nesta imagem"
4. Seja preciso com os valores encontrados
5. Se for uma nota fiscal ou cupom, extraia TODOS os itens listados"""

            analysis = await gemini_client.analyze_image(
                image_base64=image_base64,
                mime_type=mimetype,
                prompt=prompt
            )

            logger.info(f"✅ Imagem analisada com sucesso: {analysis[:100]}...")
            return analysis

        except Exception as e:
            logger.error(f"❌ Erro ao processar imagem: {e}")
            return "Desculpe, tive um problema ao analisar sua imagem. Pode tentar enviar novamente ou descrever os itens?"

    @staticmethod
    async def process_document(message_data: Dict[str, Any], message_id: str) -> str:
        """
        Processa mensagem de documento/PDF (DocumentMessage)

        Fluxo:
        1. Baixar documento via Uazapi (base64)
        2. Analisar com Google Gemini (suporta PDF)
        3. Retornar informações extraídas

        Args:
            message_data: Dados da mensagem do webhook
            message_id: ID da mensagem para download

        Returns:
            Texto com informações extraídas do documento
        """
        try:
            logger.info(f"📄 Processando documento: {message_id}")

            # 1. Baixar documento via Uazapi
            media_data = await uazapi_client.download_media(
                message_id=message_id,
                return_base64=True
            )

            document_base64 = media_data.get("base64Data")
            mimetype = media_data.get("mimetype", "application/pdf")

            if not document_base64:
                logger.error("❌ Documento não retornou base64")
                return "Não consegui processar o documento. Tente enviar novamente."

            # 2. Analisar com Gemini (suporta PDF)
            prompt = """Analise este documento e extraia todas as informações financeiras relevantes.
Identifique:
1. Descrição de produtos/serviços
2. Valores
3. Datas (se disponíveis)
4. Categorias (se identificável: alimentação, saúde, etc)

Formate como:
Comprei [item] por [valor] em [data se disponível].

Se for uma fatura ou boleto, extraia:
- Valor total
- Data de vencimento
- Descrição do serviço/produto"""

            analysis = await gemini_client.analyze_document(
                document_base64=document_base64,
                mime_type=mimetype,
                prompt=prompt
            )

            logger.info(f"✅ Documento analisado com sucesso: {analysis[:100]}...")
            return analysis

        except Exception as e:
            logger.error(f"❌ Erro ao processar documento: {e}")
            return "Desculpe, tive um problema ao analisar seu documento. Pode tentar enviar novamente ou descrever as informações?"

    @staticmethod
    async def route_and_process(
        message_type: str,
        message_data: Dict[str, Any],
        message_id: Optional[str] = None
    ) -> str:
        """
        Roteia e processa mensagem baseado no tipo

        Args:
            message_type: Tipo da mensagem (Conversation, AudioMessage, etc)
            message_data: Dados da mensagem
            message_id: ID da mensagem (necessário para mídia)

        Returns:
            Texto processado
        """
        logger.info(f"🔀 Roteando mensagem tipo: {message_type}")

        # Mapeamento de tipos para processadores
        type_mapping = {
            "conversation": MessageProcessor.process_conversation,
            "extendedtextmessage": MessageProcessor.process_extended_text,
            "audiomessage": MessageProcessor.process_audio,
            "imagemessage": MessageProcessor.process_image,
            "documentmessage": MessageProcessor.process_document,
        }

        # Normalizar tipo (lowercase)
        message_type_lower = message_type.lower()

        # Buscar processador
        processor = type_mapping.get(message_type_lower)

        if not processor:
            logger.warning(f"⚠️ Tipo de mensagem não suportado: {message_type}")
            return f"Desculpe, ainda não suporto mensagens do tipo {message_type}."

        # Processar baseado no tipo
        if message_type_lower in ["audiomessage", "imagemessage", "documentmessage"]:
            if not message_id:
                logger.error("❌ message_id necessário para processar mídia")
                return "Erro ao processar mídia: ID da mensagem não fornecido."
            return await processor(message_data, message_id)
        else:
            return await processor(message_data)


# Instância global
message_processor = MessageProcessor()
