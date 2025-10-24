"""
Integração com OpenAI API
Baseado no fluxo N8n: [FLUXO PRINCIPAL] - AudioMessage processing
"""
import base64
import io
from typing import Optional
from openai import AsyncOpenAI
from loguru import logger
from app.core.config import settings


class OpenAIClient:
    """
    Cliente para interação com OpenAI API
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.transcription_model = "whisper-1"  # Modelo correto da OpenAI

    async def transcribe_audio(
        self,
        audio_base64: str,
        filename: str = "audio.mp3",
        language: str = "pt"
    ) -> str:
        """
        Transcreve áudio usando Whisper API

        Args:
            audio_base64: Áudio em base64
            filename: Nome do arquivo (deve ter extensão correta)
            language: Idioma do áudio (pt, en, es, etc.)

        Returns:
            Texto transcrito
        """
        try:
            # Decodificar base64 para bytes
            audio_bytes = base64.b64decode(audio_base64)

            # Criar arquivo em memória
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename

            logger.info(f"🎤 Transcrevendo áudio ({len(audio_bytes)} bytes)...")

            # Transcrever usando Whisper
            transcription = await self.client.audio.transcriptions.create(
                model=self.transcription_model,
                file=audio_file,
                language=language
            )

            text = transcription.text
            logger.info(f"✅ Áudio transcrito: {text[:100]}...")
            return text

        except Exception as e:
            logger.error(f"❌ Erro ao transcrever áudio: {e}")
            raise

    async def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera resposta usando Chat Completion

        Args:
            messages: Lista de mensagens no formato OpenAI
            model: Modelo a ser usado
            temperature: Criatividade (0-1)
            max_tokens: Máximo de tokens na resposta

        Returns:
            Texto da resposta
        """
        try:
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            response_text = completion.choices[0].message.content
            logger.info(f"✅ Chat completion gerado ({len(response_text)} chars)")
            return response_text

        except Exception as e:
            logger.error(f"❌ Erro no chat completion: {e}")
            raise


# Instância global do cliente
openai_client = OpenAIClient()
