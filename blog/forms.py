from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Review, Profile


# ---------- Registro ----------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


# ---------- Posts ----------
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'cover', 'excerpt', 'content', 'status', 'tags']
        widgets = {
            # 👉 Aquí el campo tags se hace texto para poder escribir nuevos,
            #    y Django-Taggit reconocerá tags separados por coma.
            'tags': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escribe tags separados por coma (ej: zelda, nintendo, rumores)"
                }
            ),

            # 👉 El campo content ahora es grande y rectangular
            'content': forms.Textarea(
                attrs={
                    "class": "form-control content-textarea",
                    "style": "min-height:400px; width:100%; resize:vertical;",
                    "placeholder": "Escribe el contenido de tu post aquí..."
                }
            ),
        }


# ---------- Comentarios ----------
class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label="Escribe un comentario",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribe tu comentario aquí..."
            }
        )
    )

    class Meta:
        model = Comment
        fields = ['text']


# ---------- Reseñas ----------
class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        label="Calificación",
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    comment = forms.CharField(
        label="Comentario (opcional)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribe tu opinión..."
            }
        )
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']


# ---------- Perfil ----------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "name", "bio", "phone", "location", "interests"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre completo"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Escribe algo sobre ti..."}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: +507 6000-0000"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ciudad, País"}),
            "interests": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: programación, música, deportes"}),
        }
