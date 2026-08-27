from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('distributor', 'Distributor'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='distributor')

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def is_distributor_user(self):
        return self.role == 'distributor'
