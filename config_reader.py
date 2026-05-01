from enum import StrEnum, auto
from functools import lru_cache
from os import environ
from pathlib import Path
from tomllib import load
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, SecretStr, field_validator


ConfigType = TypeVar("ConfigType", bound=BaseModel)


class LogRenderer(StrEnum):
    JSON = auto()
    CONSOLE = auto()


class BotConfig(BaseModel):
    """Bot configuration."""
    token: SecretStr
    owners: list[int] = []

    @field_validator("owners", mode="before")
    @classmethod
    def parse_owners(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


class LogConfig(BaseModel):
    """Logging configuration."""
    show_datetime: bool = True
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    show_debug_logs: bool = False
    time_in_utc: bool = False
    use_colors_in_console: bool = True
    renderer: LogRenderer = LogRenderer.CONSOLE

    @field_validator("renderer", mode="before")
    @classmethod
    def log_renderer_to_lower(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v


class L10nConfig(BaseModel):
    """Localization configuration."""
    default_locale: str = "en"
    fallback_locale: str = "en"
    locales_path: str = "l10n"


class ThrottlingConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = True
    rate_limit: float = 0.5  # seconds between messages
    max_users: int = 10000  # max users to track


class Config(BaseModel):
    """Root configuration model."""
    bot: BotConfig
    logs: LogConfig = LogConfig()
    localization: L10nConfig = L10nConfig()


class MongoConfig(BaseModel):
    username: str
    password: str
    cluster_url: str
    app_name: str


class URL(BaseModel):
    url: str


def is_docker_env() -> bool:
    """Check if running in Docker environment."""
    # Check for .dockerenv file (most reliable)
    if Path("/.dockerenv").exists():
        return True
    # Fallback: check for DOCKER_ENV environment variable
    return environ.get("DOCKER_ENV", "").lower() == "true"


def get_config_path() -> Path:
    """Get configuration file path from environment or default."""
    env_path = environ.get("CONFIG_FILE_PATH")
    if env_path:
        return Path(env_path)
    return Path("config.toml")


@lru_cache
def parse_config_file() -> dict:
    """Parse TOML configuration file."""
    file_path = get_config_path()

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, "rb") as file:
        return load(file)


@lru_cache
def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    """
    Get typed configuration section.

    In Docker environment, loads from environment variables.
    Locally, loads from config.toml file.

    Args:
        model: Pydantic model class for validation
        root_key: Top-level key in config file (or env var name prefix in Docker)

    Returns:
        Validated configuration object

    Raises:
        KeyError: If root_key not found in config
    """
    if is_docker_env():
        # In Docker: load from environment variables
        config_dict = _load_config_from_env(root_key)
    else:
        # Locally: load from config.toml
        config_dict = parse_config_file()

    if root_key not in config_dict:
        raise KeyError(f"Configuration key '{root_key}' not found in config")

    return model.model_validate(config_dict[root_key])


def _load_config_from_env(root_key: str) -> dict:
    """
    Load configuration from environment variables.
    
    Expects environment variables prefixed with root_key (uppercase).
    Example: For root_key='bot', expects BOT_TOKEN, BOT_OWNERS, etc.
    """
    prefix = root_key.upper() + "_"
    config_dict = {root_key: {}}
    
    for key, value in environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):].lower()
            config_dict[root_key][config_key] = value
    
    return config_dict


def get_env_or_config(
    env_var: str,
    config_model: Type[ConfigType],
    config_key: str,
    config_attr: str,
) -> Optional[str]:
    """
    Get value from environment variable or config file.

    Environment variables always take precedence.
    In Docker: uses environment variables with proper prefix.
    Locally: falls back to config.toml values.
    """
    env_value = environ.get(env_var)
    if env_value is not None:
        return env_value

    # If in Docker, check for prefixed environment variable
    if is_docker_env():
        prefix = config_key.upper() + "_"
        docker_var = prefix + config_attr.upper()
        docker_value = environ.get(docker_var)
        if docker_value is not None:
            return docker_value
        return None

    # Locally: load from config.toml
    try:
        config = get_config(model=config_model, root_key=config_key)
        return getattr(config, config_attr, None)
    except (KeyError, FileNotFoundError):
        return None
