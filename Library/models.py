from django.db import models
from django.contrib.auth.models import AbstractUser


# User Model
class User(AbstractUser):
    # Date when the user was added; automatically set to the current date on creation
    date_of_membership = models.DateField(auto_now_add=True)
    # Field to manage whether the user account is active
    is_active = models.BooleanField(default=True)

    class Meta:
        # Custom permissions for user actions
        permissions = [
            ('can_manage_users', 'Can manage users'),  #superusers
            ('can_manage_books', 'Can manage books'),  #staff/admins
        ]

    def __str__(self):
        return self.username


# Book Model to represent library books
class Book(models.Model):
    title = models.CharField(max_length=255)  # Title of the book
    author = models.CharField(max_length=255)  # Author's name
    isbn = models.CharField(max_length=13, unique=True)  # Unique 13-character ISBN
    published_date = models.DateField()  # Publication date of the book
    available_copies = models.PositiveIntegerField()  # Number of available copies

    class Meta:
        # Permissions for managing books
        permissions = [
            ('can_manage_books', 'Can manage books'),
        ]

    def __str__(self):
        return self.title


# Transaction Model to track book borrow/return actions
class Transaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions'
    )  # Reference to the user who borrowed/returned the book
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='transactions'
    )  # Reference to the borrowed book
    checkout_date = models.DateTimeField(auto_now_add=True)  # Timestamp of borrowing
    return_date = models.DateTimeField(null=True, blank=True)  # Timestamp of return (nullable)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
