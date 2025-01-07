from django import forms
from .models import User, Book
from django.contrib.auth.forms import UserCreationForm


class UserCreationForms(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'available_copies']

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if Book.objects.filter(isbn=isbn).exists():
            raise forms.ValidationError("A book with this ISBN already exists.")
        return isbn