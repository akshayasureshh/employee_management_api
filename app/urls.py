from django.contrib import admin
from django.urls import path, include
from .views import LoginView, CreateUserView, LogoutView, RefreshTokenView, EmployeeViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')


urlpatterns = [
    path('create_user/', CreateUserView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    path('', include(router.urls)),
]
