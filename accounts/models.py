from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    Custom User Model.
    """
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    class Meta:
        db_table = 'users'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class PendingEmail(models.Model):
    """
    Store Pending Email.
    """
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="pending_email")
    email = models.EmailField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pending_email'
        verbose_name = _("Pending Email")
        verbose_name_plural = _("Pending Emails")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} → {self.email}"