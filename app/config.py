"""Configuration models for the intranet application."""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any, Mapping


def load_env_config() -> dict[str, Any]:
    """Load configuration from environment variables."""

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LDAP_SERVER": os.getenv("LDAP_SERVER", "ldap://localhost"),
        "LDAP_BASE_DN": os.getenv("LDAP_BASE_DN", "dc=example,dc=com"),
        "LDAP_USER_DN": os.getenv("LDAP_USER_DN", "ou=users"),
        "LDAP_BIND_DN": os.getenv("LDAP_BIND_DN", ""),
        "LDAP_BIND_PASSWORD": os.getenv("LDAP_BIND_PASSWORD", ""),
        "ORACLE_DSN": os.getenv("ORACLE_DSN", ""),
        "ORACLE_USERNAME": os.getenv("ORACLE_USERNAME", ""),
        "ORACLE_PASSWORD": os.getenv("ORACLE_PASSWORD", ""),
    }


@dataclass
class Config:
    secret_key: str = "dev"
    log_level: str = "INFO"
    ldap_server: str = "ldap://localhost"
    ldap_base_dn: str = "dc=example,dc=com"
    ldap_user_dn: str = "ou=users"
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""
    oracle_dsn: str = ""
    oracle_username: str = ""
    oracle_password: str = ""

    def model_dump(self) -> dict[str, Any]:
        return {k.upper(): v for k, v in asdict(self).items()}

    @classmethod
    def from_flask(cls, mapping: Mapping[str, Any]) -> "Config":
        data = {}
        for field in asdict(cls()):
            data[field] = mapping.get(field.upper(), getattr(cls, field, None))
        return cls(**data)
