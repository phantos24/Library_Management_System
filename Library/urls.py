from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from rest_framework.routers import DefaultRouter

# Create a router for API endpoints and register the BookViewSet
router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')

# URL patterns for the application
urlpatterns = [
    # Route for the homepage
    path('', views.homepage, name='homepage'),
    
    # Route for user registration
    path('register/', views.register, name='register'),
    
    # Routes for login and logout using Django's built-in authentication views
    path('login/', auth_views.LoginView.as_view(template_name='homepage.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Route for the main hall page where users can view and borrow books
    path('main_hall/', views.main_hall, name='main_hall'),
    
    # Route for the "My Books" page where users can view their borrowed books
    path('my_books/', views.my_books, name='my_books'),
    
    # Include routes from the router for the REST API
    path('', include(router.urls)),
    
    # API endpoint for listing books with optional filters
    path('api/books/', views.BookListAPIView.as_view(), name='book_list_api'),
    
    # Route for managing books (admins)
    path('manage_books/', views.manage_books, name='manage_books'),
    
    # Route for editing a specific book by its ID
    path('manage_books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    
    # Route for managing users (superusers only)
    path('manage_users/', views.manage_users, name='manage_users'),
]
