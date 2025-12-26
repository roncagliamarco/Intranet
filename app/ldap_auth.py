"""Simple LDAP authentication helper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flask_login import UserMixin
from ldap3 import Connection, Server, ALL, ALL_ATTRIBUTES

from .config import Config


@dataclass
class User(UserMixin):
    username: str
    display_name: str | None = None

    def get_id(self) -> str:
        return self.username


class LdapAuthenticator:
    """Authenticate users against an LDAP server."""

    def __init__(self, config: Config):
        self.config = config

    def authenticate(self, username: str, password: str) -> Optional[User]:
        server = Server(self.config.ldap_server, get_info=ALL)
        user_dn = f"cn={username},{self.config.ldap_user_dn},{self.config.ldap_base_dn}"
        bind_dn = self.config.ldap_bind_dn or user_dn
        bind_password = self.config.ldap_bind_password or password

        with Connection(
            server,
            user=bind_dn,
            password=bind_password,
            auto_bind=True,
        ) as conn:
            conn.search(user_dn, "(objectclass=person)", attributes=ALL_ATTRIBUTES)
            if not conn.entries:
                return None
            display_name = conn.entries[0].displayName.value if conn.entries else username
            return User(username=username, display_name=display_name)

    def get_user(self, username: str) -> Optional[User]:
        # For demo purposes we do not persist users; recreate the object on demand
        return User(username=username)
