from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import SignUpForm, PostForm, CommentForm, ReviewForm, ProfileForm
from .models import Post, Comment, Review

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

# --------- Detalle / Comentarios / Reviews / Moderación ----------
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comment_form'] = CommentForm()
        ctx['review_form'] = ReviewForm()
        return ctx

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    form = CommentForm(request.POST or None)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user
        c.is_approved = False
        c.save()
        messages.info(request, 'Comentario enviado. Espera moderación del autor.')
    return redirect(post.get_absolute_url())

@login_required
def moderate_comment(request, pk, action):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.post.author != request.user:
        messages.error(request, 'No puedes moderar comentarios de posts ajenos.')
        return redirect(comment.post.get_absolute_url())
    if action == 'approve':
        comment.is_approved = True
        comment.save()
        messages.success(request, 'Comentario aprobado.')
    elif action == 'reject':
        comment.delete()
        messages.warning(request, 'Comentario rechazado y eliminado.')
    return redirect(comment.post.get_absolute_url())

@login_required
def add_review(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data.get('comment', '')
        obj, created = Review.objects.get_or_create(
            post=post, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            obj.rating = rating
            obj.comment = comment
            obj.save()
            messages.info(request, 'Actualizaste tu calificación.')
        else:
            messages.success(request, '¡Gracias por calificar!')
    else:
        messages.error(request, 'Revisa el formulario de review.')
    return redirect(post.get_absolute_url())

# --------- CRUD con permisos ----------
class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

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
def profile_detail(request):
    return render(request, 'profile/detail.html')

@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado.')
        return redirect('blog:profile')
    return render(request, 'profile/edit.html', {'form': form})
