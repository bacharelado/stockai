"""Cliente isolado para comunicação com o provedor de IA."""

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL


class AIProviderError(RuntimeError):
    """Erro controlado na comunicação com o provedor de IA."""


class AIClient:
    def __init__(self) -> None:
        if not OPENAI_API_KEY:
            raise AIProviderError("Integração de IA não configurada: defina OPENAI_API_KEY.")
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    def gerar_resposta(self, *, instrucoes: str, entrada: str) -> str:
        try:
            response = self._client.responses.create(
                model=OPENAI_MODEL,
                instructions=instrucoes,
                input=entrada,
            )
        except Exception as exc:  # O endpoint converte isso em erro controlado.
            raise AIProviderError("Não foi possível consultar o serviço de IA.") from exc

        texto = (response.output_text or "").strip()
        if not texto:
            raise AIProviderError("O serviço de IA não retornou uma resposta de texto.")
        return texto
