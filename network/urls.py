
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('following/', views.following, name='following'),

    path("create-post", views.create_post, name="create_post"),
    path('comment/<int:post_id>/create/', views.create_comment, name='create_comment'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('like-post/<int:post_id>/<str:action>/', views.like_post, name='like_post'),
]
