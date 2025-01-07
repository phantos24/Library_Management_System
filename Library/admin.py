from django.contrib import admin
from .models import User, Book, Transaction

# Register your models here.

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Transaction)
