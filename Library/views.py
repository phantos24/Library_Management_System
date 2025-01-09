from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, filters
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import User, Book, Transaction
from .Serializers import UserSerializer, BookSerializer, TransactionSerializer
from .forms import UserCreationForms, BookForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import login
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.

#Homepage view
def homepage(request):
    # If the user is authenticated, redirect them to another page.
    if request.user.is_authenticated:
        return redirect('main_hall')

    # Initialize the authentication form
    form = AuthenticationForm()

    # Render the homepage template
    return render(request, 'homepage.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('main_hall')

    if request.method == 'POST':
        form = UserCreationForms(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately after registration
            return redirect('homepage')  # Redirect to homepage or another page
    else:
        form = UserCreationForms()
    return render(request, 'register.html', {'form': form})

@login_required
def main_hall(request):
    available_only = request.GET.get('available_only', False)
    # Get the filter parameters from the request
    title = request.GET.get('title', None)
    author = request.GET.get('author', None)
    isbn = request.GET.get('isbn', None)

    # Filter the books based on the query parameters
    books = Book.objects.all()

    if title:
        books = books.filter(title__icontains=title)  # Case-insensitive search for title
    if author:
        books = books.filter(author__icontains=author)  # Case-insensitive search for author
    if isbn:
        books = books.filter(isbn__icontains=isbn)  # Case-insensitive search for ISBN

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            messages.error(request, "The book does not exist.")
            return redirect('main_hall')

        # Check if the user already has an active transaction for this book
        existing_transaction = Transaction.objects.filter(
            user=request.user, book=book, return_date__isnull=True).exists()

        if existing_transaction:
            messages.error(request, "You have already borrowed a copy of this book.")
        elif book.available_copies > 0:
            # Create a transaction and reduce the available copies of the book
            Transaction.objects.create(user=request.user, book=book)
            book.available_copies -= 1
            book.save()
            messages.success(request, f"You have successfully borrowed '{book.title}'.")
        else:
            messages.error(request, "No copies of this book are currently available.")

        return redirect('main_hall')
    
    if available_only:
        books = books.filter(available_copies__gt=0)

    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main_hall.html', {'page_obj': page_obj})

@login_required
def my_books(request):
    # Get both borrowed and returned books
    borrowed_books = Transaction.objects.filter(user=request.user).order_by('-checkout_date')

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        if transaction and not transaction.return_date:
            # Set the return date to mark the book as returned
            transaction.return_date = timezone.now()
            transaction.save()

            # Increment the available copies for the returned book
            book = transaction.book
            book.available_copies += 1
            book.save()

            return redirect('my_books')
        
    # Pagination
    paginator = Paginator(borrowed_books, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_books.html', {'page_obj': page_obj})

# Ensure that only admin (is_staff but not is_superuser) users can manage books
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def manage_books(request):
    books = Book.objects.all()

    if request.method == 'POST':
        if 'add' in request.POST:
            form = BookForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Book added successfully!")
                return redirect('manage_books')
            else:
                messages.error(request, "Failed to add the book. there is a book with the same ISBN in the library.")

        elif 'edit' in request.POST:
            book_id = request.POST.get('book_id')
            book = get_object_or_404(Book, id=book_id)
            form = BookForm(request.POST, instance=book)
            if form.is_valid():
                form.save()
                messages.success(request, "Book updated successfully!")
                return redirect('manage_books')
            else:
                messages.error(request, "Failed to update the book. Please check the details.")


        elif 'delete' in request.POST:
            book_id = request.POST.get('book_id')
            book = get_object_or_404(Book, id=book_id)
           
            if Transaction.objects.filter(book=book, return_date__isnull=True).exists():
                messages.error(request, "Cannot delete this book because it is currently borrowed.")
                return redirect('manage_books')

            # If the book is not borrowed, proceed with deletion
            book.delete()
            messages.success(request, "Book deleted successfully!")
            return redirect('manage_books')
        
    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_books.html', {'page_obj': page_obj, 'form': BookForm()})

# Only superusers can manage users
@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = User.objects.all()

    if request.method == 'POST':
        if 'create' in request.POST:
            form = UserCreationForms(request.POST)
            if form.is_valid():
                new_user = form.save()
                messages.success(request, f"User '{new_user.username}' created successfully!")
                return redirect('manage_users')
            else:
                messages.error(request, "Failed to create the user. Please check the details.")
        
        elif 'edit' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            form = UserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, f"User '{user.username}' updated successfully!")
                return redirect('manage_users')
            else:
                messages.error(request, "Failed to update the user. Please check the details.")
        
        elif 'delete' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user == request.user:  # Prevent deletion of the currently logged-in user
                messages.error(request, "You cannot delete your own account.")
                return redirect('manage_users')
            user.delete()
            messages.success(request, "User deleted successfully!")
            return redirect('manage_users')

        elif 'toggle_admin' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.is_staff = not user.is_staff  # Toggle the admin status
            user.save()
            status = "admin" if user.is_staff else "user"
            messages.success(request, f"User '{user.username}' is now a {status}.")
            return redirect('manage_users')
        
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_users.html', {'page_obj': page_obj, 'form': UserCreationForms()})

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('manage_books')  # Redirect to the manage books page after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'edit_book.html', {'form': form, 'book': book})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['available_copies']  # For filtering by availability
    search_fields = ['title', 'author', 'isbn']  # For searching by title, author, or ISBN

    def get_queryset(self):
        # Filter books with available copies if `available=true` is passed in query params
        queryset = super().get_queryset()
        available = self.request.query_params.get('available')
        if available == 'true':
            queryset = queryset.filter(available_copies__gt=0)
        return queryset

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class BookListAPIView(APIView):
    def get(self, request):
        # Get query parameters
        title = request.GET.get('title', None)
        author = request.GET.get('author', None)
        isbn = request.GET.get('isbn', None)

        # Filter the books based on the query parameters
        books = Book.objects.all()

        if title:
            books = books.filter(title__icontains=title)  # Case-insensitive search for title
        if author:
            books = books.filter(author__icontains=author)  # Case-insensitive search for author
        if isbn:
            books = books.filter(isbn__icontains=isbn)  # Case-insensitive search for isbn

        # Serialize the filtered books
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
