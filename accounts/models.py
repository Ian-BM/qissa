from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from .phone import PhoneValidationError, validate_african_phone
class UserManager(BaseUserManager):
    def create_user(self, phone, name=None):
        if not phone:
            raise ValueError("Phone number is required")
        
        try:
            normalized_phone = validate_african_phone(phone)
        except PhoneValidationError as exc:
            raise ValueError(str(exc)) from exc

        user = self.model(
        phone=normalized_phone,
            name=name or ""
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password=None):
        user = self.create_user(phone, name)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    def clean(self):
        super().clean()
        try:
            self.phone = validate_african_phone(self.phone)
        except PhoneValidationError as exc:
            raise ValidationError({"phone": str(exc)}) from exc


    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.phone
