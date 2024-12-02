# Poe API Bots

## 项目简介 (Project Overview)

这是一个基于 FastAPI 和 Langchain 的多模型 Poe 聊天机器人框架，支持 OpenAI 和 Ollama 模型。

This is a multi-model Poe chatbot framework based on FastAPI and Langchain, supporting OpenAI and Ollama models.

## 特性 (Features)

- 🤖 支持多种 AI 模型 (Support multiple AI models)
- 🔧 灵活的配置管理 (Flexible configuration management)
- 📝 详细的日志系统 (Comprehensive logging system)
- 🚀 快速部署 (Easy deployment)

## 配置文件示例 (Configuration File Example)

```toml
listen_host = "0.0.0.0"
listen_port = 51245
log_level = "INFO"
console_log_level = "INFO"
file_log_level = "INFO"
log_file_path = "./logs/app.log"
[[bot_configs]]
model = "gpt-4o"
api_base = "https://api.openai.com/v1"
api_key = "your_api_key"
poe_key = "your_poe_key"
bot_type = "openai"
host = "http://localhost:11434"
history_length = 10
sub_url = "/bot"
bot_name = "test_bot"
```

## 安装依赖 (Install Dependencies)

```bash
pip install -r requirements.txt
```

或者使用 `uv` 安装 (Using `uv` to install)

```bash
uv pip install -e .
```

## 运行项目 (Run Project)

```bash
uv run bot/bot.py -c ./configs/config.toml
```

```bash
python3 bot/bot.py -c ./configs/config.toml
```

```
docker run -d -p 51245:51245 -v ./logs:/app/logs -v ./configs:/app/configs nerdneils/poe-api-bots:latest
```

## 支持的命令 (Supported Commands)

- `/start` - 启动对话 (Start conversation)
- `/version` - 查看版本 (View version)
- `/help` - 显示帮助信息 (Show help information)

## 环境要求 (Requirements)

- Python 3.10+
- FastAPI
- Langchain
- Poe API

## 贡献 (Contribution)

欢迎提交 PR 和 Issues！(Welcome to submit PRs and Issues!)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=nerdneils/poe-api-bots&type=Date)](https://star-history.com/#nerdneils/poe-api-bots&Date)


## License

[MIT](LICENSE)