from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_unique_nickname(nickname, instance=None):
    queryset = Profile.objects.exclude(pk=instance.pk) if instance else Profile.objects.all()
    if queryset.filter(nickname=nickname).exists():
        raise ValidationError(f"Nickname '{nickname}' is already taken.")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, unique=True)
    max_spend = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    def __str__(self):
        return self.user.username
    
    def clean(self):
        validate_unique_nickname(self.nickname, instance=self)
#playing around

    def save(self, *args, **kwargs):
        self.max_spend = self.balance
        self.clean()
        super().save(*args, **kwargs)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('top-up', 'Top-up'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='top-up')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} for {self.user.username}"

    @staticmethod
    def get_balance(user):
        total_top_up = Transaction.objects.filter(user=user, transaction_type='top-up').aggregate(total=models.Sum('amount'))['total'] or user.profile.balance
        return total_top_up
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)