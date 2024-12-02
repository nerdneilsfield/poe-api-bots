from abc import ABC, abstractmethod
from typing import AsyncIterable, Tuple, List, override
from enum import Enum, auto


import fastapi_poe as fp
from pydantic import BaseModel, Field
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from log_utils import get_logger

class BotType(Enum):
    OPENAI = auto()
    OLLAMA = auto()

class BaseBotConfig(BaseModel):
    bot_type: BotType = Field(default=BotType.OPENAI)
    bot_name: str = Field(default="")
    model: str = Field(default="gpt-4o")
    api_base: str = Field(default="https://api.openai.com/v1")
    api_key: str = Field(default="")
    poe_key: str = Field(default="")
    host: str = Field(default="http://localhost:11434")
    history_length: int = Field(default=10)
    temperature: float = Field(default=0.7)
    # for ollama: Max number of tokens to generate.
    num_predict: int = Field(default=1024)


class BaseBot(fp.PoeBot):
    """
    Base class for all the bots

    Args:
    config (BaseBotConfig): The config for the bot
    """

    def __init__(self, config: BaseBotConfig):
        """
        Initializes the bot

        Args:
        config (BaseBotConfig): The config for the bot
        """
        self.config = config
        # self.bot_name = config.bot_name
        self.access_key = config.poe_key
        self.chat_model = self.init_model()
        
        self.logger = get_logger(config.bot_name)
        self.logger.info(f"Bot {config.bot_name} initialized")

    @abstractmethod
    def init_model(self):
        """
        Initializes the chat model

        Returns:
        The initialized chat model
        """
        pass

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        """
        Gets the response for the given request

        Args:
        request (fp.QueryRequest): The query request

        Returns:
        The response as an async iterable of partial responses
        """
        last_query = request.query[-1]
        if self.is_command(last_query.content):
            self.logger.debug(f"Bot {self.config.bot_name} received command: {last_query.content}")
            async for response in self.handle_bot_command(last_query.content):
                yield response
            return

        messages = self._prepare_messages(request)

        async for chunk in self.chat_model.astream(messages):
            self.logger.debug(f"Bot {self.config.bot_name} generated chunk: {chunk.content}")
            yield fp.PartialResponse(text=chunk.content)

    def _prepare_messages(self, request: fp.QueryRequest) -> List[HumanMessage | SystemMessage | AIMessage]:
        """
        Prepares the messages for the given request

        Args:
        request (fp.QueryRequest): The query request

        Returns:
        The prepared messages
        """
        messages = []
        querys = (
            request.query[len(request.query) - self.config.history_length :]
            if len(request.query) > self.config.history_length
            else request.query
        )
        for message in querys:
            content = message.content
            if message.role == "user" and not self.is_command(content):
                messages.append(HumanMessage(content=content))
            elif message.role == "system":
                messages.append(SystemMessage(content=content))
            elif message.role == "bot":
                messages.append(AIMessage(content=content))
        return messages

    async def handle_bot_command(
        self, command: str
    ) -> AsyncIterable[fp.PartialResponse]:
        """
        处理不同的 Bot 命令
        """
        if command == "/version":
            self.logger.debug(f"Bot {self.config.bot_name} received command: {command}")
            yield fp.PartialResponse(
                text=f"Current version is 0.0.1", is_suggested_reply=False
            )
        elif command == "/changelog":
            self.logger.debug(f"Bot {self.config.bot_name} received command: {command}")
            yield fp.PartialResponse(text="changelog", is_suggested_reply=False)
        elif command == "/start":
            self.logger.debug(f"Bot {self.config.bot_name} received command: {command}")
            yield fp.PartialResponse(
                text="welcome to use this bot!，use /help to get more information",
                is_suggested_reply=False,
            )
        elif command == "/help":
            self.logger.debug(f"Bot {self.config.bot_name} received command: {command}")
            yield fp.PartialResponse(
                text="this is help information", is_suggested_reply=False
            )
        else:
            self.logger.debug(f"Bot {self.config.bot_name} received unsupported command: {command}")
            yield fp.PartialResponse(
                text="unsupported command!", is_suggested_reply=False
            )

    def is_command(self, message: str) -> bool:
        return message.startswith("/")


class OllamaBot(BaseBot):
    @override
    def init_model(self):
        return ChatOllama(
            model=self.config.model,
            host=self.config.host or "http://localhost:11434",
            temperature=self.config.temperature,
            num_predict=self.config.num_predict,
        )


class OpenaiBot(BaseBot):
    @override
    def init_model(self):
        return ChatOpenAI(
            model=self.config.model,
            api_key=self.config.api_key,
            base_url=self.config.api_base or "https://api.openai.com/v1",
            temperature=self.config.temperature,
            max_tokens=self.config.num_predict
        )
        

class BotFactory:
    @staticmethod
    def create_bot(config: BaseBotConfig) -> BaseBot:
        if config.bot_type == BotType.OPENAI:
            return OpenaiBot(config)
        elif config.bot_type == BotType.OLLAMA:
            return OllamaBot(config)
        else:
            raise ValueError(f"Unsupported bot type: {config.bot_type}")
