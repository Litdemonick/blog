from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from taggit.models import Tag
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager
from django.db.models import Q


# ----------------------------
# Perfil de usuario
# ----------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name="Biografía")

    # 🔹 Nuevos campos añadidos
    name = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Nombre completo",
        help_text="Tu nombre real o el que quieras mostrar públicamente."
    )
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        verbose_name="Teléfono",
        help_text="Número de contacto (opcional)."
    )
    location = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Ubicación",
        help_text="Ciudad o país donde te encuentras."
    )
    interests = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Intereses",
        help_text="Ej: Programación, Música, Deportes..."
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'


# ----------------------------
# Post (noticia o rumor)
# ----------------------------

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )

    PLATFORM_CHOICES = [
        ("pc", "PC"),
        ("xbox", "Xbox"),
        ("nintendo", "Nintendo Switch"),
        ("mobile", "Celular"),
        ("ps", "PlayStation"),
        
    ]

    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    is_visible = models.BooleanField(default=True)  # 👈 nuevo campo
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="pc")
    excerpt = models.CharField(max_length=300, blank=True)
    content = RichTextUploadingField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        """Genera slug único automáticamente."""
        if not self.slug:
            base = slugify(self.title)[:200] or 'post'
            candidate = base
            i = 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base[:200 - len(str(i)) - 1]}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return round(agg['avg'] or 0, 2)

    @property
    def total_reviews(self):
        return self.reviews.count()


# ----------------------------
# Comentarios (moderados por autor del post)
# ----------------------------

class Comment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("visible", "Visible"),
        ("hidden", "Oculto"),
        ("blocked", "Bloqueado"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="comments"
    )
    text = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)
    
    is_reaction = models.BooleanField(default=True)

    # 🔹 Nuevo: relación para respuestas
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    # 🔹 Nuevo: moderador puede fijar comentarios
    pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pinned", "-created"]  # 👈 fijados arriba, luego por fecha


    def __str__(self):
        return f"Comentario de {self.author} en {self.post}"

    @property
    def score(self):
        upvotes = self.votes.filter(value=1).count()
        downvotes = self.votes.filter(value=-1).count()
        return upvotes - downvotes

    @property
    def likes_count(self):
        return self.votes.filter(value=1).count()

    @property
    def dislikes_count(self):
        return self.votes.filter(value=-1).count()


# ----------------------------
# Votos en comentarios
# ----------------------------

class CommentVote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
        (0, 'Neutral'),
    )

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_votes")
    value = models.SmallIntegerField(choices=VOTE_CHOICES, default=0)

    class Meta:
        unique_together = ("comment", "user")

    def __str__(self):
        return f"{self.user.username} votó {self.value} en comentario {self.comment.id}"


# ----------------------------
# Reseñas (con rating y moderación)
# ----------------------------

class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("visible", "Visible"),
        ("hidden", "Oculto"),
        ("blocked", "Bloqueado"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    rating = models.PositiveSmallIntegerField(
    
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )  # ⭐ Puede ser vacío si es solo respuesta
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.user} – {self.comment[:30]}"

    @property
    def likes_count(self):
        return self.votes.filter(vote="like").count()

    @property
    def dislikes_count(self):
        return self.votes.filter(vote="dislike").count()


# ----------------------------
# Votos en reseñas (like / dislike)
# ----------------------------

class ReviewVote(models.Model):
    VOTE_CHOICES = (
        ('like', '👍'),
        ('dislike', '👎'),
    )

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    vote = models.CharField(max_length=7, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.vote} en {self.review}"


# ----------------------------
# Bloqueo de notificaciones entre usuarios
# ----------------------------

class NotificationBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_notifications")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="muted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked_user")

    def __str__(self):
        return f"{self.blocker.username} bloqueó notificaciones de {self.blocked_user.username}"


# ----------------------------
# Bloqueo de usuarios en posts
# ----------------------------

class PostBlock(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="blocks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_in_posts")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} bloqueado en {self.post}"


# ----------------------------
# Notificaciones
# ----------------------------

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")  # El que recibe
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")  # El que actúa
    verb = models.CharField(max_length=255)  # Ej: "comentó tu post"

    target_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    target_review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True)
    target_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.verb} → {self.user}"

    def get_absolute_url(self):
        """Redirige según el target disponible."""
        if self.target_comment:
            return self.target_comment.post.get_absolute_url() + f"#comment-{self.target_comment.id}"
        elif self.target_review:
            return self.target_review.post.get_absolute_url() + f"#review-{self.target_review.id}"
        elif self.target_post:
            return self.target_post.get_absolute_url()
        return "#"


# ----------------------------
# Reacciones (emojis) en posts
# ----------------------------
# Opciones de reacciones (emojis)
REACTION_CHOICES = [
    ('like', '👍'),
    ('love', ''),
    ('funny', '😂'),
    ('wow', '😮'),
    ('sad', '😢'),
    ('angry', '😡'),
]
class Reaction(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    rating = models.IntegerField(null=True, blank=True)   # 👈 opcional
    opinion = models.TextField(null=True, blank=True)  # 👈 opcional
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")  # 👈 un usuario solo puede reaccionar una vez a un post
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} reaccionó {self.type} a {self.post}"


class Subscription(models.Model):
    """
    Una suscripción apunta a EXACTAMENTE un objetivo:
    - un autor (User)
    - o un tag   (Tag)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="author_followers")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True, related_name="tag_followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evitar duplicados y forzar que sólo uno (author o tag) esté definido
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], condition=Q(tag__isnull=True),
                name="uniq_user_author_subscription"
            ),
            models.UniqueConstraint(
                fields=["user", "tag"], condition=Q(author__isnull=True),
                name="uniq_user_tag_subscription"
            ),
            models.CheckConstraint(
                check=(
                    (Q(author__isnull=False) & Q(tag__isnull=True)) |
                    (Q(author__isnull=True) & Q(tag__isnull=False))
                ),
                name="one_target_either_author_or_tag"
            ),
        ]

    def __str__(self):
        if self.author_id:
            return f"{self.user.username} → Autor:{self.author.username}"
        return f"{self.user.username} → Tag:{self.tag.slug}"