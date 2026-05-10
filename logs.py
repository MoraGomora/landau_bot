from datetime import datetime
import logging

from collections import deque
from json import dumps
from typing import Any

import structlog
from structlog import WriteLoggerFactory

from config_reader import LogConfig, LogRenderer
from utils import save_logs


logs_buffer: deque[str] = deque(maxlen=100)


def file_processor(logger, method, event_dict):
    """Structlog processor to write log messages to file."""
    now = datetime.now().strftime("%Y-%m-%d")

    path = save_logs(logs_buffer, f"logs/{now}.log")
    if not path:
        logger.warning("Failed to save logs to file.")
    
    return event_dict


def buffer_processor(logger, method_name, event_dict):
    """Structlog processor to buffer log messages."""
    logs_buffer.append(event_dict.copy())
    return event_dict


def get_structlog_config(log_config: LogConfig) -> dict[str, Any]:
    """
    Build structlog configuration dictionary.

    Args:
        log_config: Log configuration object

    Returns:
        Configuration dict for structlog.configure()
    """
    min_level = logging.DEBUG if log_config.show_debug_logs else logging.INFO

    return {
        "processors": get_processors(log_config),
        "cache_logger_on_first_use": True,
        "wrapper_class": structlog.make_filtering_bound_logger(min_level),
        "logger_factory": WriteLoggerFactory(),
    }


def get_processors(log_config: LogConfig) -> list:
    """
    Build list of structlog processors.

    Args:
        log_config: Log configuration object

    Returns:
        List of processor functions
    """

    def custom_json_serializer(data: dict, *args, **kwargs) -> str:
        """Custom JSON serializer with ordered keys."""
        result = {}

        if log_config.show_datetime and "timestamp" in data:
            result["timestamp"] = data.pop("timestamp")

        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        result.update(**data)
        return dumps(result, default=str)

    processors = []

    if log_config.show_datetime:
        processors.append(
            structlog.processors.TimeStamper(
                fmt=log_config.datetime_format,
                utc=log_config.time_in_utc,
            )
        )

    processors.append(structlog.processors.add_log_level)
    processors.append(buffer_processor)
    processors.append(file_processor)
    
    if log_config.renderer == LogRenderer.JSON:
        processors.append(
            structlog.processors.JSONRenderer(serializer=custom_json_serializer)
        )
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=log_config.use_colors_in_console,
                pad_level=True,
            )
        )

    return processors
