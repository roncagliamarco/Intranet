from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

try:
    from ldap3 import Connection, Server, ALL
except Exception:  # pragma: no cover - ldap is optional at runtime
    Connection = None
    Server = None
    ALL = None


class LdapBackend(BaseBackend):
    """Autenticazione LDAP con fallback demo se LDAP non è configurato."""

    def authenticate(self, request, username: Optional[str] = None, password: Optional[str] = None, **kwargs):
        if not username or not password:
            return None

        ldap_config = settings.LDAP_CONFIG
        server_uri = ldap_config.get('SERVER')
        base_dn = ldap_config.get('BASE_DN')
        user_dn = ldap_config.get('USER_DN')

        if server_uri and Connection and Server:
            server = Server(server_uri, get_info=ALL)
            bind_dn = ldap_config.get('BIND_DN')
            bind_password = ldap_config.get('BIND_PASSWORD')
            user_principal = f"cn={username},{user_dn},{base_dn}" if user_dn else f"cn={username},{base_dn}"
            try:
                with Connection(server, user=bind_dn or user_principal, password=bind_password or password, auto_bind=True) as conn:
                    if bind_dn:
                        if not conn.rebind(user=user_principal, password=password):
                            return None
                    return self._get_or_create_user(username)
            except Exception:
                return None

        # Demo fallback: permetti login con qualsiasi credenziale in assenza di LDAP
        return self._get_or_create_user(username)

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_or_create_user(self, username):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        return user
