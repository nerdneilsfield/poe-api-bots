from logger import LoggerManager, FastAPILogMiddleware, set_logger_manager, get_logger_manager, log_method
from configs import AppConfig
from models import BotFactory

import argparse

from fastapi import FastAPI
import fastapi_poe as fp

def main(app_config: AppConfig) -> FastAPI:

    main_app = FastAPI()
    logger = get_logger_manager().get_logger("main")

    for bot_config in app_config.bot_configs:
        logger.info(f"Creating bot for {bot_config.name}")
        bot = BotFactory.create_bot(bot_config.to_bot_config())
        bot_app = fp.make_app(bot)
        main_app.mount(bot_config.sub_url, bot_app)
        
    return main_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server mutlitple Poe server bots with different models")
    parser.add_argument("-c","--config", type=str, default="./configs/config.toml", help="Path to the configuration file")
    
    # LoggerManager.add_logger_arguments(parser)
    
    args = parser.parse_args()
    
    app_config = AppConfig.load_config(args.config)
    
    main_app = main(app_config)
    
    logger_manager = LoggerManager.from_app_config(app_config)
    set_logger_manager(logger_manager)
    
    logger = get_logger_manager().get_logger("main")
    
    logger.info(f"Starting server on {app_config.listen_host}:{app_config.listen_port}")
    
    main_app.add_middleware(FastAPILogMiddleware, logger_manager=logger_manager)
    
    import uvicorn
    
    uvicorn.run(main_app, host=app_config.listen_host, port=app_config.listen_port)
    
    