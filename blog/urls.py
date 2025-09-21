from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_by_tag'),
    path('buscar/', views.PostListView.as_view(), name='search'),

    path('post/nuevo/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/editar/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/eliminar/', views.PostDeleteView.as_view(), name='post_delete'),

    path('post/<slug:slug>/comentar/', views.add_comment, name='add_comment'),
    path('comentario/<int:pk>/<str:action>/', views.moderate_comment, name='moderate_comment'),

    path('post/<slug:slug>/review/', views.add_review, name='add_review'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile_detail, name='profile'),
    path('profile/editar/', views.profile_edit, name='profile_edit'),
]
