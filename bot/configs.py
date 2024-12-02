from models import BaseBotConfig, BotType

import os
from pathlib import Path
import toml
from pydantic import BaseModel, Field
from typing import Optional, List


class BotConfig(BaseModel):
    """
    Configuration for a single bot
    """

    model: str = Field(..., description="AI model name")  # AI model name
    api_base: Optional[str] = Field(None, description="API base URL")  # API base URL
    api_key: Optional[str] = Field(None, description="API key")  # API key
    poe_key: Optional[str] = Field(None, description="POE key")  # POE key
    bot_type: str = Field(default="openai", description="Bot type")  # Bot type
    bot_name: Optional[str] = Field(None, description="Bot name")  # Bot name
    host: Optional[str] = Field(
        default="http://localhost:11434", description="Model server host"
    )  # Model server host
    history_length: int = Field(
        10, description="Number of messages to keep in history"
    )  # Number of messages to keep in history
    sub_url: Optional[str] = Field(
        default="/bot", description="Sub URL for this bot"
    )  # Sub URL for this bot
    
    
    def to_bot_config(self) -> BaseBotConfig:
        """
        Convert the bot config to a BaseBotConfig
        """
        
        model_type = BotType.OPENAI
        if self.bot_type == "openai":
            model_type = BotType.OPENAI
        elif self.bot_type == "ollama":
            model_type = BotType.OLLAMA
        else:
            raise ValueError(f"Invalid bot type: {self.bot_type}")
    
        return BaseBotConfig(
            model=model_type,
            api_base=self.api_base,
            api_key=self.api_key,
            history_length=self.history_length,
            host=self.host,
            poe_key=self.poe_key,
            bot_name=self.bot_name,
        )


class AppConfig(BaseModel):
    """
    Configuration for the application
    """

    listen_host: str = Field(
        default="0.0.0.0", description="Host to listen on"
    )  # Host to listen on
    listen_port: int = Field(
        default=51245, description="Port to listen on"
    )  # Port to listen on
    log_level: Optional[str] = Field(
        default="INFO", description="Log level for the application"
    )  # Log level for the application
    console_log_level: Optional[str] = Field(
        default="INFO", description="Log level for the console"
    )  # Log level for the console
    file_log_level: Optional[str] = Field(
        default="INFO", description="Log level for the log file"
    )  # Log level for the log file
    log_file_path: Optional[str] = Field(
        default="./logs/app.log", description="Path to the log file"
    )  # Path to the log file
    bot_configs: List[BotConfig] = Field(
        default_factory=list, description="List of bot configurations"
    )  # List of bot configurations

    @classmethod
    def load_config(cls, config_path: str = None):
        """
        Load the configuration from the given file
        """
        print(f"Loading config from {config_path}")
        if config_path is None:
            config_path = "./configs/config.toml"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        config_dict = toml.load(config_path)
        return cls(**config_dict)

    @classmethod
    def generate_example_config(cls, output_path: Path = None):
        """
        Generate an example configuration file
        """
        example_config = cls(
            listen_host="0.0.0.0",
            listen_port=51245,
            bot_configs=[
                BotConfig(
                    model="gpt-4o",
                    bot_type="openai",
                    sub_url="/bot",
                    history_length=10,
                    host="http://localhost:11434",
                    api_base="https://api.openai.com/v1",
                    api_key="your_api_key",
                    poe_key="your_poe_key",
                    temperature=0.7,
                    num_predict=2048,
                ).model_dump()
            ],
        )
        if output_path is None:
            output_path = Path(__file__).parent.parent / "configs/example_config.toml"

        parent_dir = os.path.dirname(output_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(output_path, "w") as f:
            toml.dump(example_config.model_dump(), f)
