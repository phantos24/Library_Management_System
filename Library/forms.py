from django import forms
from .models import User, Book
from django.contrib.auth.forms import UserCreationForm


# Custom user creation form
class UserCreationForms(UserCreationForm):
    # Adding required fields for first name, last name, and email
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Links the form to the custom User model
        fields = ['first_name', 'last_name', 'email', 'username']  # Fields included in the form


# Form for managing Book model operations (e.g., create, update)
class BookForm(forms.ModelForm):
    class Meta:
        model = Book  # Links the form to the Book model
        fields = ['title', 'author', 'isbn', 'published_date', 'available_copies']  # Fields included in the form

    # Custom validation method to ensure unique ISBNs for books
    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        # Check if a book with the same ISBN exists, excluding the current instance (for updates)
        if Book.objects.filter(isbn=isbn).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A book with this ISBN already exists.")
        return isbn  # Return the cleaned ISBN
