from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Comment, PostBlock
from taggit.models import Tag
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post
from .models import Post
import re
from .models import Notification
from .models import Post, Comment, Review, ReviewVote, PostBlock
from .forms import SignUpForm, PostForm, ReviewForm, ProfileForm


from .models import (
    Post, Comment, Review, ReviewVote,
    PostBlock, Notification, NotificationBlock
)


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

# --------- Perfil ----------
def profile_detail(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect("blog:login")
        profile_user = request.user

    return render(request, "profile/detail.html", {"profile_user": profile_user})


# --------- Auth ----------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada! Bienvenido.')
            return redirect('blog:post_list')
        messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


def global_tags(request):
    return {"all_tags": Tag.objects.all()[:15]}  # mostrar solo los 15 primeros


@login_required
def vote_review(request, pk, action):
    review = get_object_or_404(Review, pk=pk)
    if action not in ['like', 'dislike']:
        messages.error(request, "Acción inválida.")
        return redirect(review.post.get_absolute_url())

    vote, created = ReviewVote.objects.get_or_create(
        review=review, user=request.user,
        defaults={'vote': action}
    )

    if not created:
        if vote.vote == action:
            vote.delete()
            messages.info(request, f"Quitaste tu {action}.")
        else:
            vote.vote = action
            vote.save()
            messages.success(request, f"Cambiaste a {action}.")
    else:
        messages.success(request, f"¡Gracias por tu {action}!")

    return redirect(review.post.get_absolute_url())



# --------- Listado / Búsqueda / Paginación ----------
class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = Post.objects.filter(status='published')
        q = self.request.GET.get('q')
        tag = self.kwargs.get('tag_slug')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs.select_related('author').prefetch_related('tags')


# --------- Detalle / Reseñas / Comentarios ----------
class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        # 🔹 Reseñas (solo principales = sin parent)
        if user.is_authenticated and (user == post.author or user.is_staff):
            ctx["reviews"] = post.reviews.filter(parent__isnull=True)
            ctx["is_owner"] = True
        else:
            ctx["reviews"] = post.reviews.filter(parent__isnull=True, status="visible")
            ctx["is_owner"] = False

        # 🔹 Comentarios (si también quieres manejarlos)
        if user.is_authenticated and (user == post.author or user.is_staff):
            ctx["comments"] = post.comments.filter(parent__isnull=True)
        else:
            ctx["comments"] = post.comments.filter(parent__isnull=True, status="visible")

        # 🔹 Formularios
        ctx["review_form"] = ReviewForm()
        # ctx["comment_form"] = CommentForm()

        return ctx


def procesar_menciones(comentario, actor, post):
    """Detecta @username en el texto del comentario y crea notificaciones (si no está bloqueado)."""
    patron = r'@(\w+)'  # Busca palabras después de @
    usernames = re.findall(patron, comentario.text)

    for uname in usernames:
        try:
            mencionado = User.objects.get(username=uname)
            if mencionado != actor:  # no notificarse a sí mismo
                # ⚡ Evitar si el usuario bloqueó al actor
                if not NotificationBlock.objects.filter(blocker=mencionado, blocked_user=actor).exists():
                    Notification.objects.create(
                        user=mencionado,
                        actor=actor,
                        verb="te mencionó en un comentario",
                        target_post=post,
                        target_comment=comentario
                    )
        except User.DoesNotExist:
            continue  # ignorar usuarios inexistentes



# --------- Añadir reseña ----------
@login_required
def add_review(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        comment = request.POST.get("comment", "").strip()
        rating = request.POST.get("rating")

        # Caso: respuesta a una reseña existente
        if parent_id:
            parent = Review.objects.filter(id=parent_id, post=post).first()
            if parent:
                reply = Review.objects.create(
                    post=post,
                    user=request.user,
                    parent=parent,
                    comment=comment,
                    status="visible"   # ✅ directo visible
                )
                # Notificación al autor original
                if parent.user != request.user:
                    Notification.objects.create(
                        user=parent.user,
                        actor=request.user,
                        verb="respondió a tu reseña",
                        target_post=post,
                        target_review=parent   # ✅ mejor referencia a la reseña padre
                    )
                messages.success(request, "Respuesta publicada.")
            return redirect(post.get_absolute_url())

        # Caso: reseña principal
        if rating:
            review = Review.objects.create(   # ✅ guardamos en variable
                post=post,
                user=request.user,
                rating=rating,
                comment=comment,
                status="visible"   # ✅ directo visible
            )
            # ⚡ Notificar al autor del post si no es el mismo
            if post.author != request.user:
                if not NotificationBlock.objects.filter(blocker=post.author, blocked_user=request.user).exists():
                    Notification.objects.create(
                        user=post.author,
                        actor=request.user,
                        verb="dejó una reseña en tu publicación",
                        target_post=post,
                        target_review=review
                    )
            messages.success(request, "¡Tu reseña fue publicada!")
        else:
            messages.error(request, "Debes dar una calificación para publicar una reseña.")

    return redirect(post.get_absolute_url())





def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")
    reviews = post.reviews.filter(parent__isnull=True, status="visible")

    context = {
        "object": post,
        "reviews": reviews,
        "is_owner": request.user == post.author,
    }
    return render(request, "blog/post_detail.html", context)





def post_by_platform(request, platform_slug):
    posts = Post.objects.filter(platform=platform_slug)
    return render(request, "post_list.html", {
        "posts": posts,
        "platform": platform_slug,
    })


# --------- Añadir comentario ----------
@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")

    # 🔒 Revisar si el usuario está bloqueado en este post
    if PostBlock.objects.filter(post=post, user=request.user).exists():
        messages.error(request, "Has sido bloqueado y no puedes comentar en este post.")
        return redirect(post.get_absolute_url())

    if request.method == "POST":
        text = request.POST.get("text")
        parent_id = request.POST.get("parent_id")

        if text:
            parent = None
            if parent_id:
                parent = Comment.objects.filter(id=parent_id).first()

            comentario = Comment.objects.create(
                post=post,
                author=request.user,
                text=text,
                parent=parent,   # ✅ guardamos el padre si existe
                status="visible"  # ✅ directo visible
            )

            # ⚡ Notificar al autor del comentario padre (si no bloqueó al actor)
            if parent and parent.author and parent.author != request.user:
                if not NotificationBlock.objects.filter(blocker=parent.author, blocked_user=request.user).exists():
                    Notification.objects.create(
                        user=parent.author,
                        actor=request.user,
                        verb="respondió a tu comentario",
                        target_post=post,
                        target_comment=comentario
                    )

            # ⚡ Notificar al autor del post principal (si no es el mismo que comenta)
            if post.author != request.user:
                if not NotificationBlock.objects.filter(blocker=post.author, blocked_user=request.user).exists():
                    Notification.objects.create(
                        user=post.author,
                        actor=request.user,
                        verb="comentó en tu publicación",
                        target_post=post,
                        target_comment=comentario
                    )

            # ✅ Procesar menciones con @usuario
            procesar_menciones(comentario, request.user, post)

            messages.success(request, "Comentario publicado.")

    return redirect(post.get_absolute_url())


@login_required
def notification_list(request):
    notifications = request.user.notifications.all().order_by("-created_at")
    return render(request, "notifications/list.html", {"notifications": notifications})




@login_required
def notification_mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    return redirect("notification_list")



# --------- CRUD con permisos ----------
class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    




@login_required
def notification_disable_user(request, user_id):
    actor = get_object_or_404(User, pk=user_id)
    NotificationBlock.objects.get_or_create(blocker=request.user, blocked_user=actor)
    messages.info(request, f"Has desactivado las notificaciones de {actor.username}.")
    return redirect("notification_list")

@login_required
def notification_enable_user(request, user_id):
    actor = get_object_or_404(User, pk=user_id)
    NotificationBlock.objects.filter(blocker=request.user, blocked_user=actor).delete()
    messages.success(request, f"Has activado nuevamente las notificaciones de {actor.username}.")
    return redirect("notification_list")



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post creado.')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Post actualizado.')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, 'Post eliminado.')
        return super().delete(request, *args, **kwargs)


# --------- Perfil ----------
@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado.')
        return redirect('blog:profile')
    return render(request, 'profile/edit.html', {'form': form})


# --------- Moderación de reseñas ----------
@login_required
def moderate_review(request, pk, action):
    review = get_object_or_404(Review, pk=pk)

    # Solo el autor del post puede moderar reseñas
    if request.user != review.post.author:
        return HttpResponseForbidden("No autorizado")

    if action == "hide":
        review.status = "hidden"
        review.save()
        messages.info(request, "Reseña ocultada.")
    elif action == "block":
        # 🔥 Toggle de bloqueo
        block, created = PostBlock.objects.get_or_create(
            post=review.post,
            user=review.user
        )
        if created:
            review.status = "blocked"
            review.save()
            messages.warning(request, f"Usuario {review.user.username} bloqueado en este post.")
        else:
            block.delete()
            messages.success(request, f"Usuario {review.user.username} desbloqueado en este post.")
    elif action == "delete":
        review.delete()
        messages.error(request, "Reseña eliminada.")
    else:
        return HttpResponseForbidden("Acción no válida")

    return redirect("blog:post_detail", slug=review.post.slug)



# --------- Moderación de comentarios ----------
from .models import Comment, PostBlock

@login_required
def moderate_comment(request, pk, action):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.post.author:
        return HttpResponseForbidden("No autorizado")

    # ❌ Quitamos "approve"
    if action == "hide":
        comment.status = "hidden"
        comment.save()
    elif action == "block":
        block, created = PostBlock.objects.get_or_create(
            post=comment.post,
            user=comment.author
        )
        if not created:
            block.delete()
        comment.status = "blocked"
        comment.save()
    elif action == "delete":
        comment.delete()
    else:
        return HttpResponseForbidden("Acción no válida")

    return redirect("blog:post_detail", slug=comment.post.slug)



@login_required
def vote_comment(request, pk, vote_type):
    comment = get_object_or_404(Comment, pk=pk)
    
    if vote_type not in ['up', 'down']:
        messages.error(request, "Acción inválida.")
        return redirect(comment.post.get_absolute_url())

    value = 1 if vote_type == "up" else -1

    vote, created = CommentVote.objects.get_or_create(user=request.user, comment=comment)
    if not created and vote.value == value:
        vote.delete()  # quitar voto si repite
    else:
        vote.value = value
        vote.save()

    return redirect(comment.post.get_absolute_url())

