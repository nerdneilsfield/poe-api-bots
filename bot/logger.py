import argparse
import logging
import sys
import os
from typing import Optional, Union
import coloredlogs
from functools import wraps
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class LoggerManager:
    """
    A logger manager to configure and manage loggers.

    Args:
        console_level (str): The logging level for the console handler.
            Defaults to 'INFO'.
        file_level (str): The logging level for the file handler.
            Defaults to 'DEBUG'.
        log_file (Optional[str]): The path to the log file. If not provided,
            no file handler will be created.
    """

    def __init__(
        self,
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        log_file: Optional[str] = "app.log",
    ):
        # Create the main logger
        self.loggers = {}

        self.console_level = console_level
        self.file_level = file_level
        self.log_file = log_file

        self.logger = self.init_logger("logger_manager")

    def colored_console_install(self, logger: logging.Logger):
        """
        Install colored logs for the console
        """
        coloredlogs.install(
            level=self.console_level.upper(),
            logger=logger,
            fmt="%(asctime)s | %(levelname)8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            field_styles={
                "asctime": {"color": "green"},
                "levelname": {"bold": True, "color": "cyan"},
                "name": {"color": "blue"},
                "filename": {"color": "magenta"},
                "lineno": {"color": "yellow"},
            },
        )

    def init_logger(self, name: Optional[str] = None):
        """
        Initialize the logger
        """

        logger = logging.getLogger(name or "bot_logger")

        print(
            f"Initializing logger for {name} with level {self.console_level} and file level {self.file_level} and log file {self.log_file}"
        )

        # Console log handler
        self.colored_console_install(logger)

        # File log handler
        if self.log_file:
            # logfile directory
            logfile_dir = os.path.dirname(os.path.abspath(self.log_file))
            if not os.path.exists(logfile_dir):
                os.makedirs(logfile_dir, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(self.file_level.upper())
            file_formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def get_logger(self, name: Optional[str] = None):
        """
        Get a logger with the given name.

        Args:
            name (Optional[str]): The logger name, defaults to None

        Returns:
            logging.Logger: The configured logger
        """
        # self.logger.debug(f"Getting logger for {name}")
        if name not in self.loggers:
            self.loggers[name] = self.init_logger(name)
        return self.loggers[name]

    def log_method(self, level="info"):
        """
        A decorator to log method calls.

        Args:
            level (str): The log level, defaults to 'info'

        Returns:
            callable: The decorated function
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger = self.get_logger(func.__module__)
                log_method = getattr(logger, level)

                # Try to get the class name
                class_name = (
                    args[0].__class__.__name__
                    if args and hasattr(args[0], "__class__")
                    else ""
                )

                log_method(f"Calling method: {class_name}.{func.__name__}")
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def add_logger_arguments(cls, parser: argparse.ArgumentParser):
        """
        Add logger-related arguments to the argument parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser
        """
        parser.add_argument(
            "-l",
            "--log-level",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the log level",
        )
        parser.add_argument(
            "--console-log-level",
            type=str,
            default=None,
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the console log level (optional)",
        )
        parser.add_argument(
            "--file-log-level",
            type=str,
            default=None,
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the file log level (optional)",
        )

    def set_log_level(
        self,
        log_level: Optional[str] = None,
        console_log_level: Optional[str] = None,
        file_log_level: Optional[str] = None,
    ):
        """
        Dynamically set the log level.

        Args:
            log_level (Optional[str]): The global log level
            console_log_level (Optional[str]): The console log level
            file_log_level (Optional[str]): The file log level
        """
        self.console_level = console_log_level
        self.file_level = file_log_level

        for name in self.loggers:
            self.loggers[name] = self.init_logger(name)

    @classmethod
    def from_args(cls, args: Union[argparse.Namespace, dict]):
        """
        Create a LoggerManager instance from command line arguments.

        Args:
            args (Union[argparse.Namespace, dict]): The command line arguments

        Returns:
            LoggerManager: The configured logger manager instance
        """
        # If it's a Namespace, convert it to a dictionary
        if hasattr(args, "__dict__"):
            args = vars(args)

        # Create the logger manager
        logger_manager = cls(
            console_level=args.get("log_level", "INFO"),
            file_level=args.get("file_log_level", "INFO"),
            log_file=args.get("log_file", None),
        )

        # If a specific console log level is specified
        if args.get("console_log_level"):
            logger_manager.set_log_level(
                console_log_level=args["console_log_level"],
                file_log_level=args["file_log_level"],
            )

        return logger_manager

    # @classmethod
    # def from_app_config(cls, app_config: AppConfig):
    #     return cls(
    #         console_level=app_config.console_log_level,
    #         file_level=app_config.file_log_level,
    #         log_file=app_config.log_file_path
    #     )


class FastAPILogMiddleware(BaseHTTPMiddleware):
    """
    A middleware to log information about incoming requests and outgoing responses.

    Args:
        app (FastAPI): The FastAPI application instance.
        logger_manager (LoggerManager): The logger manager instance.
    """

    def __init__(self, app, logger_manager: LoggerManager):
        super().__init__(app)
        self.logger = logger_manager.get_logger("fastapi")

    async def dispatch(self, request: Request, call_next):
        # Log the request information
        self.logger.info(f"Request: {request.method} {request.url}")

        # Process the request
        response: Response = await call_next(request)

        # Log the response information
        self.logger.info(f"Response: {response.status_code}")

        return response


# global logger manager
logger_manager = LoggerManager(
    console_level="DEBUG",  # console log level
    file_level="INFO",  # file log level
    log_file="",  # log file path
)


# function to get logger
def get_logger(name: Optional[str] = None):
    return logger_manager.get_logger(name)


def set_logger_manager(logger_manager_instance: LoggerManager):
    global logger_manager
    logger_manager = logger_manager_instance


def get_logger_manager():
    return logger_manager


# log method decorator
log_method = logger_manager.log_method
