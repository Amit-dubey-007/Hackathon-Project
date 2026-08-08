from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class EmailOTP(models.Model):
    REGISTER = "register"
    RESET = "reset"

    PURPOSE_CHOICES = [
        (REGISTER, "Register"),
        (RESET, "Reset Password"),
    ]
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now=True)
    resend_count = models.IntegerField(default=0)
    last_resend_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    
    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time
    
    def can_resend(self):
        if self.last_resend_time + timezone.timedelta(seconds=30) > timezone.now():
            return False
        return True
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "purpose"],
                name="unique_email_purpose"
            )
        ]
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    wallet_address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )