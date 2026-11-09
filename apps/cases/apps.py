from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class CasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cases'
    verbose_name = _('Catálogo')

