from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='homepage.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('main_hall/', views.main_hall, name='main_hall'),
    path('my_books/', views.my_books, name='my_books'),
    path('', include(router.urls)),
    path('api/books/', views.BookListAPIView.as_view(), name='book_list_api'),
    path('manage_books/', views.manage_books, name='manage_books'),
    path('manage_books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('manage_users/', views.manage_users, name='manage_users'),
]
