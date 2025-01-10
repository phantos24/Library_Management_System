from rest_framework import serializers
from .models import User, Book, Transaction


# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields to be serialized for the User model
        fields = ['id', 'username', 'email', 'date_of_membership', 'is_active']


# Serializer for the Book model
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        # Fields to be serialized for the Book model
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'available_copies']


# Serializer for the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        # Fields to be serialized for the Transaction model
        fields = ['id', 'user', 'book', 'checkout_date', 'return_date']
