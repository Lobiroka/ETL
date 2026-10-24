"""Carrega a configuração do projeto uma vez por processo."""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_URL = os.getenv("DATABASE_URL")


def require_config(name: str, value: str | None) -> str:
    if not value:
        raise ValueError(f"A variável {name} não foi definida no .env")
    return value
