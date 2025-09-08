from django.urls import path
from authentication.views import register_view, login_view, logout_view, user_management_view, user_edit_view, user_delete_view, profile_edit_view

app_name = "authentication"

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_edit_view, name='profile_edit'),

    path('users/', user_management_view, name='user_management'),
    path('users/<int:user_id>/edit/', user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', user_delete_view, name='user_delete'),
]