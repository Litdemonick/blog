from django.contrib import messages

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from .models import Comment, PostBlock
from taggit.models import Tag
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post
from .models import Post
import re
import json
from .models import Notification
from .models import Post, Comment, Review, ReviewVote, PostBlock
from .forms import SignUpForm, PostForm, ReviewForm, ProfileForm
from .models import Post, Reaction, REACTION_CHOICES
from .models import Post, Reaction, REACTION_CHOICES
from django.db.models import Count
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .serializers import ReactionSerializer
from .models import CommentVote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import logging
from .api_views import ReactionView
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@login_required
def pin_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.post.author:  # Solo el dueño del post puede fijar
        review.pinned = True
        review.save()
        messages.success(request, "Reseña fijada correctamente 📌")
    else:
        messages.error(request, "No tienes permisos para fijar esta reseña.")
    return redirect("blog:post_detail", slug=review.post.slug)


logger = logging.getLogger(__name__)

@login_required
def unpin_review(request, review_id):
    # buscar en vez de usar get() directo
    reviews_qs = Review.objects.filter(id=review_id).order_by('-created')
    count = reviews_qs.count()

    if count == 0:
        raise Http404("Review no encontrada")

    if count > 1:
        # Logueamos el problema para revisarlo/depurarlo después
        logger.warning("MultipleObjectsReturned al buscar Review id=%s: %d resultados", review_id, count)
        # tomamos la más reciente para trabajar y evitamos el 500
        review = reviews_qs.first()
    else:
        review = reviews_qs.first()

    if request.user == review.post.author:
        review.pinned = False
        review.save()
        messages.success(request, "Reseña desfijada correctamente ❌")
    else:
        messages.error(request, "No tienes permisos para desfijar esta reseña.")
    return redirect("blog:post_detail", slug=review.post.slug)


# --------- Listado / Búsqueda / Paginación ----------
from django.db.models import Count, Q
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # posts puede estar en ctx['posts'] (context_object_name) o en ctx['object_list']
        posts = ctx.get(self.context_object_name) or ctx.get('object_list') or []
        # si está paginado, posts es la lista de objetos de la página; construimos ids
        post_ids = [p.id for p in posts]

        if post_ids:
            qs = (
                Reaction.objects
                .filter(post_id__in=post_ids)
                .values('post_id', 'type')
                .annotate(count=Count('id'))
            )
            counts_map = {}
            for r in qs:
                pid = r['post_id']
                counts_map.setdefault(pid, {})[r['type']] = r['count']
        else:
            counts_map = {}

        # Adjuntar reaction_counts (diccionario) a cada post
        for p in posts:
            p.reaction_counts = counts_map.get(p.id, {})

        return ctx

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

    # Conteos de reacciones
    counts = Reaction.objects.filter(post=post).values("type").annotate(total=Count("id"))
    reaction_counts = {c["type"]: c["total"] for c in counts}
    for key, _ in REACTION_CHOICES:
        reaction_counts.setdefault(key, 0)

    context = {
        "object": post,
        "reviews": reviews,
        "is_owner": request.user == post.author,
        "reaction_counts": reaction_counts, 
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

# --------- Reacciones (emojis) ----------
from .models import Reaction
@login_required
def toggle_reaction(request, post_id):
    post = Post.objects.get(id=post_id)
    reaction_type = request.POST.get("reaction")

    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:
        if existing.type == reaction_type:
            # si el user repite la misma → se elimina
            existing.delete()
        else:
            # si cambia → se actualiza
            existing.type = reaction_type
            existing.save()
    else:
        # nueva reacción
        Reaction.objects.create(user=request.user, post=post, type=reaction_type)

    # devolver conteo actualizado
    counts = {r[0]: post.reactions.filter(type=r[0]).count() for r in dict(Reaction._meta.get_field("type").choices)}

    return JsonResponse({"success": True, "counts": counts})
# --------- Endpoint AJAX para reacciones ----------
from .models import Reaction
from django.utils import timezone
from django.db.models import Count

@require_POST
@login_required
def react_api(request):
    """
    Recibe JSON { post, type, rating? }.
    - Crea/actualiza Reaction (post,user)
    - Crea/actualiza Review automático (post,user) con texto 'Reacción automática: {type}'
    - Devuelve counts y review_html + review_id
    NO crea ni devuelve comentarios (para evitar que aparezcan en la sección Comentarios).
    """
    # parse JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON")

    post_id = data.get('post')
    rtype = data.get('type')
    rating = data.get('rating', 5)

    if not post_id or not rtype:
        return HttpResponseBadRequest("Missing 'post' or 'type'")

    # validar tipo de reacción (ajusta REACTION_CHOICES si se llama distinto)
    valid_types = set(dict(REACTION_CHOICES).keys())
    if rtype not in valid_types:
        return HttpResponseBadRequest("Invalid reaction type")

    # obtener post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponseBadRequest("Post not found")

    # crear/actualizar Reaction
    try:
        with transaction.atomic():
            reaction, created = Reaction.objects.update_or_create(
                post=post,
                user=request.user,
                defaults={'type': rtype}
            )
    except Reaction.MultipleObjectsReturned:
        qs = Reaction.objects.filter(post=post, user=request.user).order_by('id')
        reaction = qs.first()
        qs.exclude(id=reaction.id).delete()
        reaction.type = rtype
        reaction.save()
        created = False

    # crear/actualizar Review automático (asegurando que solo exista 1)
    try:
        with transaction.atomic():
            rev_qs = Review.objects.filter(post=post, user=request.user).order_by('id')
            if rev_qs.exists():
                review = rev_qs.first()
                # actualizar solo si es una reseña automática o está vacía
                if (not review.comment) or review.comment.startswith('Reacción automática:'):
                    review.comment = f'Reacción automática: {rtype}'
                    review.rating = rating
                    review.save(update_fields=['comment', 'rating'])
            else:
                review = Review.objects.create(
                    post=post,
                    user=request.user,
                    comment=f'Reacción automática: {rtype}',
                    rating=rating,
                    created=timezone.now(),
                    status='visible'
                )
    except Review.MultipleObjectsReturned:
        qs = Review.objects.filter(post=post, user=request.user).order_by('id')
        review = qs.first()
        qs.exclude(id=review.id).delete()
        if (not review.comment) or review.comment.startswith('Reacción automática:'):
            review.comment = f'Reacción automática: {rtype}'
            review.rating = rating
            review.save(update_fields=['comment', 'rating'])

    # recompute reaction counts por tipo
    qs_counts = Reaction.objects.filter(post=post).values('type').annotate(count=Count('id'))
    counts = {r['type']: r['count'] for r in qs_counts}
    for t in valid_types:
        counts.setdefault(t, 0)

    # renderizar HTML parcial de review (usa tu partial que refleje la UI de reseñas)
    # Asegúrate de tener templates/blog/partials/review_item.html
    review_html = render_to_string('blog/partials/review_item.html', {'r': review, 'user': request.user})

    return JsonResponse({
        'status': 'ok',
        'counts': counts,
        'review_html': review_html,
        'review_id': review.id,
        "counts": counts,
    })

def _find_auto_comment_qs(post, user):
    """
    Devuelve un queryset de comentarios que parecen ser comentarios automáticos
    de reacción para este (post, user). No lanzamos si el campo no existe.
    """
    qs_list = []
    try:
        qs_list.append(Comment.objects.filter(post=post, author=user))
    except Exception:
        pass
    try:
        qs_list.append(Comment.objects.filter(post=post, user=user))
    except Exception:
        pass

    # Filtrar por texto indicativo de "reacción automática"
    combined_q = None
    for qs in qs_list:
        try:
            q = qs.filter(Q(text__startswith='Reacción automática:') | Q(text__icontains='reaccionó con'))
            if combined_q is None:
                combined_q = q
            else:
                combined_q = combined_q | q
        except Exception:
            # tal vez el campo se llama 'content' o 'text' no existe
            try:
                q2 = qs.filter(Q(content__startswith='Reacción automática:') | Q(content__icontains='reaccionó con'))
                if combined_q is None:
                    combined_q = q2
                else:
                    combined_q = combined_q | q2
            except Exception:
                pass

    return combined_q if combined_q is not None else Comment.objects.none()


def _upsert_reaction_comment(post, user, text):
    """
    Crea o actualiza un comment marcado como 'is_reaction' para (post,user).
    Devuelve la instancia Comment.
    NOTA: ajusta campos (author/text/status) según tu modelo si se llaman distinto.
    """
    qs = Comment.objects.filter(post=post, author=user, is_reaction=True)
    if qs.exists():
        comment = qs.first()
        comment.text = text
        comment.status = "visible"
        comment.is_reaction = True
        comment.created = comment.created or timezone.now()
        comment.save(update_fields=['text', 'status', 'is_reaction'])
        return comment
    # crear nuevo
    return Comment.objects.create(
        post=post,
        author=user,
        text=text,
        status="visible",
        is_reaction=True,
        created=timezone.now()
    )


def _delete_reaction_comment(post, user):
    """Elimina comment automático si existe (usa si implementas toggle off)."""
    Comment.objects.filter(post=post, author=user, is_reaction=True).delete()

# ---------- toggle_reaction (actualiza para borrar comentario si la reacción se elimina) ----------
@login_required
def toggle_reaction(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    reaction_type = request.POST.get("reaction")

    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:
        if existing.type == reaction_type:
            # Repite la misma → se elimina la reacción y el comentario automático
            existing.delete()
            _delete_reaction_comment(post, request.user)
        else:
            # Cambia → actualizamos reacción + comentario automático
            existing.type = reaction_type
            existing.save()
            _upsert_reaction_comment(post, request.user, f"Reacción automática: {reaction_type}")
    else:
        # Nueva → crear reacción + comentario automático
        Reaction.objects.create(user=request.user, post=post, type=reaction_type)
        _upsert_reaction_comment(post, request.user, f"Reacción automática: {reaction_type}")

    # devolver conteos
    valid_types = set(dict(REACTION_CHOICES).keys())
    counts = {r[0]: post.reactions.filter(type=r[0]).count()
              for r in dict(Reaction._meta.get_field("type").choices)}
    return JsonResponse({"success": True, "counts": counts})



# ---------- react_api (función AJAX) ----------
@login_required
def react_api(request):
    """
    Endpoint AJAX que crea/actualiza la reacción del usuario a un post,
    y crea/actualiza un comentario automático (en lugar de crear duplicados).
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=403)

    # parsear JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON")

    post_id = data.get('post')
    rtype = data.get('type')
    rating = data.get('rating', 5)

    if not post_id or not rtype:
        return HttpResponseBadRequest("Missing 'post' or 'type'")

    valid_types = set(dict(REACTION_CHOICES).keys())
    if rtype not in valid_types:
        return HttpResponseBadRequest("Invalid reaction type")

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponseBadRequest("Post not found")

    # crear o actualizar la reacción (manejo de duplicados ya lo hicimos antes)
    from django.db import transaction
    try:
        with transaction.atomic():
            reaction, created = Reaction.objects.update_or_create(
                post=post,
                user=request.user,
                defaults={'type': rtype}
            )
    except Reaction.MultipleObjectsReturned:
        qs = Reaction.objects.filter(post=post, user=request.user).order_by('id')
        reaction = qs.first()
        qs.exclude(id=reaction.id).delete()
        reaction.type = rtype
        reaction.save()
        created = False

    # Crear o actualizar el comentario automático (no crear duplicados)
    emoji = dict(REACTION_CHOICES).get(rtype, "👍")
    review_text = f"{request.user.username} reaccionó {emoji}"
    comment_text = f"Reacción automática: {emoji}"  # <-- usa el emoji aquí
    _upsert_reaction_comment(post, request.user, comment_text)
    
    # devolver conteos actualizados por tipo
    qs = Reaction.objects.filter(post=post).values('type').annotate(count=Count('id'))
    counts = {r['type']: r['count'] for r in qs}
    for t in valid_types:
        counts.setdefault(t, 0)

    return JsonResponse({
        'counts': counts,
        'redirect_url': post.get_absolute_url() + "#comments"
    })


# ---------- ReactionView (DRF) ----------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class ReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get("post")
        if not post_id:
            return Response({"error": "Se requiere el ID del post"}, status=status.HTTP_400_BAD_REQUEST)

        post = get_object_or_404(Post, id=post_id)

        serializer = ReactionSerializer(
            data=request.data,
            context={"request": request, "post": post}
        )
        serializer.is_valid(raise_exception=True)
        reaction = serializer.save()

        # 🔹 En vez de comentario → reseña
        review_text = f"{request.user.username} reaccionó con {reaction.type}"
        _upsert_reaction_review(post, request.user, review_text)

        return Response(ReactionSerializer(reaction).data, status=status.HTTP_201_CREATED)

    from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def reaction_users(request, post_id, reaction_type):
    """
    Devuelve en JSON todos los usuarios que reaccionaron con un emoji específico.
    """
    valid_types = set(dict(REACTION_CHOICES).keys())
    if reaction_type not in valid_types:
        return HttpResponseBadRequest("Invalid reaction type")

    post = get_object_or_404(Post, id=post_id)
    reactions = Reaction.objects.filter(post=post, type=reaction_type).select_related("user")

    users = [r.user.username for r in reactions]
    return JsonResponse({"users": users})