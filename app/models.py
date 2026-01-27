from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .exception import DetailErrorException
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.conf import settings


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_jwt_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        
class Employee(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name=_("User")
    )
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.user.email}"
    