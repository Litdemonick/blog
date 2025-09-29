from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.models import User
from taggit.models import Tag
from django.db.models import Q
from blog.models import Tag

from .models import Subscription, Post


def _next_url(request, default='blog:post_list'):
    """Obtiene la URL a la que redirigir tras la acción."""
    return (
        request.POST.get('next')
        or request.GET.get('next')
        or request.META.get('HTTP_REFERER')
        or redirect(default).url
    )


@login_required
def my_subscriptions(request):
    """
    Lista de suscripciones del usuario actual, separadas por autor y por tag.
    """
    subs = Subscription.objects.filter(user=request.user).select_related("author", "tag")
    author_subs = subs.filter(author__isnull=False)
    tag_subs = subs.filter(tag__isnull=False)

    return render(request, "subscriptions/my_subscriptions.html", {
        "author_subs": author_subs,
        "tag_subs": tag_subs,
    })


@login_required
def my_personal_feed(request):
    """
    Feed personalizado: posts publicados por autores seguidos o con tags seguidos.
    """
    followed_authors = Subscription.objects.filter(
        user=request.user, author__isnull=False
    ).values_list("author_id", flat=True)

    followed_tags = Subscription.objects.filter(
        user=request.user, tag__isnull=False
    ).values_list("tag_id", flat=True)

    posts = (
        Post.objects.filter(status="published")
        .filter(Q(author_id__in=followed_authors) | Q(tags__in=followed_tags))
        .distinct()
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created")
    )

    return render(request, "subscriptions/my_feed.html", {"posts": posts})


# 🔹 Toggle suscripción a autor
@require_POST
@login_required
def subscribe_author(request, username):
    author = get_object_or_404(User, username=username)
    sub = Subscription.objects.filter(user=request.user, author=author, tag=None)

    if sub.exists():
        sub.delete()
        messages.success(request, f"Has dejado de seguir a {author.username}")
    else:
        Subscription.objects.create(user=request.user, author=author)
        messages.success(request, f"Ahora sigues a {author.username}")

    return redirect(_next_url(request))


# 🔹 Toggle suscripción a tag
@require_POST
@login_required
def subscribe_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    sub = Subscription.objects.filter(user=request.user, tag=tag, author=None)

    if sub.exists():
        sub.delete()
        messages.success(request, f"Has dejado de seguir el tag #{tag.name}")
    else:
        Subscription.objects.create(user=request.user, tag=tag)
        messages.success(request, f"Ahora sigues el tag #{tag.name}")

    return redirect(_next_url(request))


@require_POST
@login_required
def unsubscribe_author(request, username):
    """Quitar de la lista de autores seguidos (Subscription)."""
    author = get_object_or_404(User, username=username)
    Subscription.objects.filter(user=request.user, author=author).delete()
    messages.success(request, f"Has dejado de seguir a {author.username}")
    return redirect(_next_url(request, "blog:my_subscriptions"))

@require_POST
@login_required
def unsubscribe_tag(request, slug):
    """Quitar de la lista de tags seguidos (Subscription)."""
    tag = get_object_or_404(Tag, slug=slug)
    Subscription.objects.filter(user=request.user, tag=tag).delete()
    messages.success(request, f"Has dejado de seguir el tag #{tag.name}")
    return redirect(_next_url(request, "blog:my_subscriptions"))