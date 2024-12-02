import logging
from logger import LoggerManager, FastAPILogMiddleware, set_logger_manager, get_logger_manager, log_method
from configs import AppConfig, get_logger_manager_from_config
from models import BotFactory

import argparse

from fastapi import FastAPI
import fastapi_poe as fp


def main(app_config: AppConfig) -> FastAPI:

    logger = get_logger_manager().get_logger("main")
    

    bots = []
    for bot_config in app_config.bot_configs:
        logger.info(f"Creating bot for {bot_config.bot_name}")
        bot = BotFactory.create_bot(bot_config.to_bot_config())
        bots.append(bot)
        
    main_app = fp.make_app(bots)
    
    
    @main_app.get("/")
    def root():
        return {"message": "Hello World"}
    
    @main_app.get("/health")
    def health():
        return {"status": "ok"}

        
    return main_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server mutlitple Poe server bots with different models")
    parser.add_argument("-c","--config", type=str, default="./configs/config.toml", help="Path to the configuration file")
    
    # LoggerManager.add_logger_arguments(parser)
    
    args = parser.parse_args()
    
    app_config = AppConfig.load_config(args.config)
    
    main_app = main(app_config)
    
    logger_manager = get_logger_manager_from_config(app_config)
    set_logger_manager(logger_manager)
    
    logger = get_logger_manager().get_logger("main")
    
    logger.info(f"Starting server on {app_config.listen_host}:{app_config.listen_port}")
    
    main_app.add_middleware(FastAPILogMiddleware, logger_manager=logger_manager)
    
    import uvicorn
    
    log_level = logging.INFO
    
    if app_config.console_log_level == "DEBUG":
        log_level = logging.DEBUG
    elif app_config.console_log_level == "INFO":
        log_level = logging.INFO
    elif app_config.console_log_level == "WARNING":
        log_level = logging.WARNING
    elif app_config.console_log_level == "ERROR":
        log_level = logging.ERROR
    elif app_config.console_log_level == "CRITICAL":
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    
    uvicorn.run(main_app, host=app_config.listen_host, port=app_config.listen_port, log_level=log_level)
    
    