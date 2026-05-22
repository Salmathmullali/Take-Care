from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    decorated = login_required(
        user_passes_test(lambda u: u.is_staff)(view_func)
    )
    return decorated


def charity_party_required(get_connection):
    """Decorator factory: ensures user is a party on an accepted connection."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            connection = get_connection(request, *args, **kwargs)
            from charity.services import connections

            if not connections.user_is_party(connection, request.user):
                raise PermissionDenied
            from charity.constants import ConnectionStatus
            if connection.status != ConnectionStatus.ACCEPTED:
                raise PermissionDenied
            return view_func(request, connection=connection, *args, **kwargs)

        return login_required(_wrapped)

    return decorator
