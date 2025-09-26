from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from . import views

app_name = "blog"


urlpatterns = [
    # --------- Posts ----------
    
    path("", views.PostListView.as_view(), name="post_list"),
    path("tag/<slug:tag_slug>/", views.PostListView.as_view(), name="post_by_tag"),
    path("buscar/", views.PostListView.as_view(), name="search"),

    path("post/nuevo/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/editar/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<slug:slug>/eliminar/", views.PostDeleteView.as_view(), name="post_delete"),

    # --------- Plataformas ----------
    path("plataforma/<str:platform_slug>/", views.post_by_platform, name="post_by_platform"),

    # --------- Reseñas ----------
    path("post/<slug:slug>/review/", views.add_review, name="add_review"),
    path("review/<int:pk>/<str:action>/vote/", views.vote_review, name="vote_review"),
    path("review/<int:pk>/<str:action>/moderate/", views.moderate_review, name="moderate_review"),

    # --------- Comentarios ----------
    path("post/<slug:slug>/comentar/", views.add_comment, name="add_comment"),
    path("comment/<int:pk>/<str:action>/moderate/", views.moderate_comment, name="moderate_comment"),

    # --------- Perfiles ----------
    path("perfil/", views.profile_detail, name="profile"),  # perfil propio
    path("perfil/editar/", views.profile_edit, name="profile_edit"),
    path("perfil/<str:username>/", views.profile_detail, name="profile_detail"),  # perfil ajeno

    # --------- Auth ----------
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # --------- Notificaciones ----------

    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", views.notification_mark_read, name="notification_mark_read"),
]
