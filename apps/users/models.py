from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(unique=True)

    steam_username = models.CharField(max_length=100, blank=True, default='', verbose_name=_('usuario de Steam'))
