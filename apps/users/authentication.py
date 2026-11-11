from django.contrib.auth import authenticate, get_user_model


def authenticate_identifier(identifier, password, request=None):
    if '@' in identifier:
        users = get_user_model()._default_manager
        # Preserve existing usernames that look like email addresses.
        if not users.filter(username=identifier).exists():
            matches = list(users.filter(email__iexact=identifier).values_list('username', flat=True)[:2])
            if len(matches) == 1:
                identifier = matches[0]

    return authenticate(request, username=identifier, password=password)
