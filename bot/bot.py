from __future__ import annotations

import logging
from argparse import ArgumentParser
from typing import AsyncIterable
import re

import coloredlogs
import fastapi_poe as fp
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from configs import API_BASE, API_KEY, MODEL, POE_KEY, HISTORY_LENGTH, CHANGELOG, VERSION

glogger = None

def is_command(input_str: str) -> bool:
    command_regex = re.compile(r"^\/\S+$")
    if command_regex.match(input_str):
        return True
    return False

class LangchainOpenAIChatBot(fp.PoeBot):
    def __init__(self):
        super().__init__()
        self.chat_model = ChatOpenAI(
            model_name=MODEL, api_key=API_KEY, openai_api_base=API_BASE
        )

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        messages = []
        querys = request.query[len(request.query) - HISTORY_LENGTH:] if len(request.query) > HISTORY_LENGTH else request.query
        
        
        if is_command(querys[-1].content):
            glogger.debug(f"is command {querys[-1].content}")
            command = querys[-1].content.split(" ")[0]
            if command == "/version":
                yield fp.PartialResponse(text=f"current version is {VERSION}", is_suggested_reply=False)
            elif command == "/changelog":
                yield fp.PartialResponse(text=CHANGELOG, is_suggested_reply=False)
            else:
                yield fp.PartialResponse(text="unspported command!", is_suggested_reply=False)
        else:
            for message in querys:
                if message.role == "bot" and (message.content != str(VERSION) and message.content != CHANGELOG):
                    messages.append(AIMessage(content=message.content))
                elif message.role == "system":
                    messages.append(SystemMessage(content=message.content))
                elif message.role == "user" and (not is_command(message.content)):
                    messages.append(HumanMessage(content=message.content))
                    
            glogger.debug(f"receive request from {request.user_id} and content is {request.query[-1].content}")
            glogger.debug(f"complete message is {messages}")

            for chunk in self.chat_model.stream(messages):
                yield fp.PartialResponse(text=chunk.content)
            
    async def deal_with_command(self, command: str) -> AsyncIterable[fp.PartialResponse]:
        pass
    async def on_error(self, error_request: fp.ReportErrorRequest) -> None:
        glogger.error(f"run in err: {error_request}")
        

def fastapi_app():
    bot = LangchainOpenAIChatBot()
    app = fp.make_app(bot, access_key=POE_KEY)
    return app

def setup_global_logger(debug: bool):
    logger = logging.getLogger(f'{MODEL} bot')
    if debug:
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')
    else:
        logger.setLevel(logging.INFO)  # 设置日志级别
        coloredlogs.install(level='INFO', logger=logger, fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')
    return logger


if __name__ == "__main__":
    
    args_parser = ArgumentParser(description="a simple bot for poe")
    
    args_parser.add_argument("-v", "--verbose", action="store_true", help="show more detailed")
    args_parser.add_argument("-p", "--port", type=int, default=51245, help="listening port")
    args_parser.add_argument("--host", type=str, default="0.0.0.0", help="listening host")
    
    args = args_parser.parse_args()
    
    glogger = setup_global_logger(args.verbose)
    
    import uvicorn

    uvicorn.run(fastapi_app(), host=args.host, port=args.port)
