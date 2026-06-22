from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils.text import slugify

from .phone import PhoneValidationError, validate_phone
class UserManager(BaseUserManager):
    def create_user(self, phone, name=None):
        if not phone:
            raise ValueError("Phone number is required")
        
        try:
            normalized_phone = validate_phone(phone)
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
            self.phone = validate_phone(self.phone)
        except PhoneValidationError as exc:
            raise ValidationError({"phone": str(exc)}) from exc


    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.phone


class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    pen_name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True, max_length=140)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="author_profiles/", blank=True, null=True
    )
    facebook_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    tiktok_link = models.URLField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["pen_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.pen_name) or "author"
            slug = base_slug
            counter = 1
            while Author.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.pen_name

    @property
    def published_story_count(self):
        return self.stories.filter(is_published=True).count()


class AuthorApplication(models.Model):
    full_name = models.CharField(max_length=120)
    pen_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    facebook_link = models.URLField(blank=True)
    audience_size = models.CharField(max_length=120, blank=True)
    genre = models.CharField(max_length=120, blank=True)
    sample_story = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pen_name} ({self.full_name})"
