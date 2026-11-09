from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UserBuilder:
    """Construye instancias de User paso a paso (Fluent Interface).

    El objeto devuelto por build() está validado pero SIN GUARDAR: quien
    orquesta el flujo (UserService) decide cuándo llamar a .save(), típicamente
    dentro de una transacción junto con la creación de recursos relacionados
    (ej. la billetera inicial). Esto evita que el Builder tome decisiones de
    persistencia que le corresponden a la capa de aplicación.
    """

    def __init__(self, user_model=None):
        self.user_model = user_model or get_user_model()
        self._username = None
        self._email = None
        self._password = None

    def con_username(self, username):
        self._username = username
        return self

    def con_email(self, email):
        self._email = email
        return self

    def con_password(self, password):
        self._password = password
        return self

    def _validar(self):
        errores = []
        if not self._username:
            errores.append(_('El username es obligatorio'))
        if not self._email:
            errores.append(_('El email es obligatorio'))
        if not self._password:
            errores.append(_('El password es obligatorio'))
        elif len(self._password) < 8:
            errores.append(_('La contraseña debe tener al menos 8 caracteres'))
        else:
            candidato = self.user_model(username=self._username, email=self._email)
            try:
                validate_password(self._password, candidato)
            except ValidationError as exc:
                errores.extend(exc.messages)
        if errores:
            raise ValueError(' / '.join(errores))

    def build(self):
        """Valida los datos acumulados y devuelve un User listo para persistir
        (sin guardar todavía: no llama a .save())."""
        self._validar()
        user = self.user_model(username=self._username, email=self._email)
        user.set_password(self._password)
        user.is_active = True
        return user
