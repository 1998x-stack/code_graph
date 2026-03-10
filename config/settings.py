# config/settings.py
# ── 全局配置，从 .env 或环境变量自动加载 ──────────────────────────────
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── OpenAI ───────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.1

    # ── 日志 ─────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/code_graph.log"

    # ── 存储 ─────────────────────────────────────────────
    GRAPH_SAVE_PATH: str = "./output/graph.pkl"

    # ── 解析 ─────────────────────────────────────────────
    # 遍历项目时跳过的目录
    EXCLUDE_DIRS: list[str] = [
        "__pycache__", ".git", "venv", "env",
        ".venv", "dist", "build", ".idea", ".vscode", "node_modules",
    ]


# 全局单例 —— 其他模块直接 from config.settings import settings
settings = Settings()