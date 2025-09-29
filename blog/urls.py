from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_subscriptions
from . import views_subscriptions as subs
from . import views
from .views import PostListView, MisPostsListView
from .views import ReactionView
from .feeds import AuthorFeed, TagFeed 

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
    path("post/<int:post_id>/reaction/", views.toggle_reaction, name="toggle_reaction"),
    path("api/react/", views.react_api, name="react_api"),
    path("post/<int:post_id>/reaction-users/<str:reaction_type>/", views.reaction_users, name="reaction_users"),

    # --------- Plataformas ----------
    path("plataforma/<str:platform_slug>/", views.post_by_platform, name="post_by_platform"),

    # --------- Reseñas ----------
    path("post/<slug:slug>/review/", views.add_review, name="add_review"),
    path("review/<int:pk>/<str:action>/vote/", views.vote_review, name="vote_review"),
    path("review/<int:pk>/<str:action>/moderate/", views.moderate_review, name="moderate_review"),

    # --------- Comentarios ----------
    path("post/<slug:slug>/comentar/", views.add_comment, name="add_comment"),
    path("comment/<int:pk>/<str:action>/moderate/", views.moderate_comment, name="moderate_comment"),

    # ---------- Votos de comentarios ----------
    path("comment/<int:pk>/vote/<str:vote_type>/", views.vote_comment, name="vote_comment"),

    # --------- Perfiles ----------
    path("perfil/", views.profile_detail, name="profile"),  # perfil propio
    path("perfil/editar/", views.profile_edit, name="profile_edit"),
    path("perfil/mis-posts/", views.my_published_posts, name="mis_posts_publicados"),

    # --------- Auth ----------
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # --------- Notificaciones ----------
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", views.notification_mark_read, name="notification_mark_read"),
    path("notifications/disable/<int:user_id>/", views.notification_disable_user, name="notification_disable_user"),
    path("notifications/enable/<int:user_id>/", views.notification_enable_user, name="notification_enable_user"),
    path("notifications/mark-read/", views.mark_all_notifications_read, name="mark_all_notifications_read"),

    # --------- Comentarios de respuestas (opcional AJAX/formulario) ----------
    path("post/<slug:slug>/comentar/respuesta/", views.add_comment, name="add_comment_reply"),

    # --------- Reseñas de respuestas (opcional) ----------
    path("post/<slug:slug>/review/respuesta/", views.add_review, name="add_review_reply"),

    path("review/<int:review_id>/pin/", views.pin_review, name="pin_review"),
    path("review/<int:review_id>/unpin/", views.unpin_review, name="unpin_review"),

    # --------- Feeds ----------
    path("feeds/author/<str:username>/", AuthorFeed(), name="author_feed"),
    path("feeds/tag/<slug:slug>/", TagFeed(), name="tag_feed"),

    # --------- Suscripciones (toggle) ----------
    path("subscribe/author/<str:username>/", subs.subscribe_author, name="subscribe_author"),
    path("subscribe/tag/<slug:slug>/", subs.subscribe_tag, name="subscribe_tag"),

    # --------- Suscripciones: páginas del usuario ----------
    path("suscripciones/", subs.my_subscriptions, name="my_subscriptions"),
    path("mi-feed/", subs.my_personal_feed, name="my_personal_feed"),
    path("suscripciones/unfollow/<str:username>/", views_subscriptions.unsubscribe_author, name="unsubscribe_author"),
    path("suscripciones/unfollow/tag/<slug:slug>/", views_subscriptions.unsubscribe_tag, name="unsubscribe_tag"),

    path("post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("post/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    path("my-drafts/", views.my_drafts, name="my_drafts"),

    # --------- Publicados ----------
    path("post/<int:post_id>/eliminar/", views.delete_post, name="eliminar_post"),
    path("post/<int:post_id>/toggle-visibility/", views.toggle_visibility, name="toggle_visibility"),


    # --------- Perfil ajeno (siempre al final porque captura todo) ----------
    path("perfil/<str:username>/", views.profile_detail, name="profile_detail"),

    path("post/<int:post_id>/toggle-visibility/", views.toggle_visibility, name="toggle_visibility"),
    path('', PostListView.as_view(), name='post_list'),
    path('mis-posts/', MisPostsListView.as_view(), name='mis_posts'),

]
