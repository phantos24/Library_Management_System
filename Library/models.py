from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# User Model
class User(AbstractUser):
    date_of_membership = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ('can_manage_users', 'Can manage users'),  # Superusers only
            ('can_manage_books', 'Can manage books'),  # Admins
        ]
    
    def __str__(self):
        return self.username

# Book Model
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    available_copies = models.PositiveIntegerField()

    class Meta:
        permissions = [
            ('can_manage_books', 'Can manage books'),
        ]
    
    def __str__(self):
        return self.title

# Transaction Model
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
