"""Load YAML config + environment overrides."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_yaml_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or _repo_root() / "configs" / "default.yaml"
    if not cfg_path.exists():
        return {}
    with cfg_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    ais_default_model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        alias="AIS_DEFAULT_MODEL",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        alias="OLLAMA_BASE_URL",
    )
    ollama_api_key: str = Field(default="ollama", alias="OLLAMA_API_KEY")
    ais_memory_dir: str = Field(default="./memory/store", alias="AIS_MEMORY_DIR")
    ais_chroma_path: str = Field(default="./memory/chroma", alias="AIS_CHROMA_PATH")
    ais_sessions_dir: str = Field(default="./sessions", alias="AIS_SESSIONS_DIR")
    ais_workspace: str = Field(default=".", alias="AIS_WORKSPACE")
    ais_log_level: str = Field(default="INFO", alias="AIS_LOG_LEVEL")
    ais_log_dir: str = Field(default="./logs", alias="AIS_LOG_DIR")


@lru_cache
def get_env() -> EnvSettings:
    return EnvSettings()


class AppConfig:
    """Merged view of YAML + environment."""

    def __init__(self, yaml_cfg: dict[str, Any] | None = None) -> None:
        self._yaml = yaml_cfg if yaml_cfg is not None else load_yaml_config()
        self.env = get_env()
        self.root = _repo_root()

    @property
    def workspace(self) -> Path:
        raw = os.getenv("AIS_WORKSPACE") or self._yaml.get("app", {}).get(
            "workspace", self.env.ais_workspace
        )
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def default_model(self) -> str:
        return (
            os.getenv("AIS_DEFAULT_MODEL")
            or self._yaml.get("models", {}).get("default")
            or self.env.ais_default_model
        )

    @property
    def openrouter_base_url(self) -> str:
        return (
            os.getenv("OPENROUTER_BASE_URL")
            or self._yaml.get("models", {}).get("openrouter_base_url")
            or self.env.openrouter_base_url
        )

    @property
    def openrouter_api_key(self) -> str:
        return self.env.openrouter_api_key

    @property
    def model_routing(self) -> dict[str, str]:
        return dict(self._yaml.get("models", {}).get("routing", {}))

    @property
    def chroma_path(self) -> Path:
        raw = self._yaml.get("memory", {}).get("chroma_path", self.env.ais_chroma_path)
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def markdown_memory_dir(self) -> Path:
        raw = self._yaml.get("memory", {}).get("markdown_dir", "./memory/notes")
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def sessions_dir(self) -> Path:
        raw = self.env.ais_sessions_dir
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def logs_dir(self) -> Path:
        raw = self.env.ais_log_dir
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def agent_permissions(self) -> dict[str, bool]:
        return dict(self._yaml.get("agents", {}).get("permissions", {}))

    @property
    def memory_settings(self) -> dict[str, Any]:
        return dict(self._yaml.get("memory", {}))

    @property
    def max_agent_retries(self) -> int:
        return int(self._yaml.get("agents", {}).get("max_retries", 2))

    def yaml_section(self, *keys: str) -> Any:
        node: Any = self._yaml
        for k in keys:
            if not isinstance(node, dict):
                return None
            node = node.get(k)
        return node


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()
