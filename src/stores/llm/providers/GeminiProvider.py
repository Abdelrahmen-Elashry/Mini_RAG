from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum
from google import genai
from google.genai import types
from stores.llm.templates.template_parser import TemplateParser

import logging

class GeminiProvider(LLMInterface):

    def __init__(self, api_key: str, template_parser: TemplateParser,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1,
                 ):

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.template_parser = template_parser

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = genai.Client(api_key=self.api_key)

        self.enums = GeminiEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = [],
                      max_output_tokens: int = None, temperature: float = None):

        if not self.client:
            self.logger.error("Gemini generation model was not set — call set_generation_model() first")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            return None

        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=GeminiEnums.USER.value)
        )

        # Override generation config per-call if custom values were provided
        generation_config = types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            system_instruction=self.template_parser.get("rag", "system_prompt")
        )

        try:
            response = self.client.models.generate_content(
                model=self.generation_model_id,
                contents=chat_history,
                config=generation_config,
            )
        except Exception as e:
            self.logger.error(f"Error while generating text with Gemini: {e}")
            return None

        if not response or not response.candidates:
            self.logger.error("Empty response received from Gemini")
            return None

        return response.text

    def embed_text(self, text: str, document_type: str = None):

        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set — call set_embedding_model() first")
            return None

        # Map DocumentTypeEnum values to Gemini task_type strings
        task_type = self._resolve_task_type(document_type)

        try:
            response = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=self.process_text(text),
                config=types.EmbedContentConfig(task_type=task_type),
            )
        except Exception as e:
            self.logger.error(f"Error while embedding text with Gemini: {e}")
            return None

        if not response or not response.embeddings:
            self.logger.error("No embedding returned from Gemini")
            return None

        return response.embeddings[0].values

    def construct_prompt(self, prompt: str, role: str):
        """
        Gemini expects:  {"role": "user" | "model", "parts": ["text"]}
        """
        return types.Content(
            role=role,
            parts=[types.Part(text=prompt)]
        )

    def _resolve_task_type(self, document_type: str) -> str:
        if document_type == DocumentTypeEnum.QUERY.value:
            return GeminiEnums.QUERY.value
        return GeminiEnums.DOCUMENT.value
