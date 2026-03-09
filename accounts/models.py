from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',         'Admin'),
        ('industry_user', 'Industry User'),
    ]

    full_name    = models.CharField(max_length=150)
    email        = models.EmailField(unique=True)
    password     = models.CharField(max_length=255)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='industry_user')
    organization = models.CharField(max_length=150, blank=True, null=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
