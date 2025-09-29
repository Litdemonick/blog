# 📰 Blog Django – Autenticación, Autorización y Contenido Enriquecido

Proyecto académico y profesional desarrollado en **Django** que implementa un sistema de blog completo con autenticación de usuarios, autorización por roles, CRUD de publicaciones, comentarios con moderación, sistema de reviews y enriquecimiento de contenido.  

Este proyecto fue desarrollado por el equipo **Los5Furiosos**:  
*Carlos Miranda, Eddie Man, Eliecias Cubilla, Harold Morales y Brayan Quintero.*

---

## 🚀 Características principales

### 🔑 Autenticación y autorización
- Registro y login con correo/usuario y contraseña.
- Logout seguro (requiere POST por defecto).
- Redirección tras crear cuenta o cerrar sesión.
- Perfiles de usuario con avatar y bio.
- Control de permisos y roles (usuario, autor, moderador, administrador).

### 📝 Gestión de publicaciones (CRUD)
- Crear, leer, editar y eliminar posts.
- Solo el autor puede editar o eliminar su propio contenido.
- Integración con **ckeditor** para texto enriquecido.
- Subida de imágenes mediante **ImageField**.
- Etiquetas y categorías con **django-taggit**.
- Paginación y búsqueda integrada.

### 💬 Comentarios con moderación
- Los usuarios pueden comentar en los posts.
- Moderación avanzada para el autor del post:
  - 🔒 Bloquear → marcar como inapropiado.
  - 👁 Ocultar → quitar de la vista pública sin borrar.
  - 👁‍🗨 Mostrar → volver visible.
  - 🗑 Eliminar → borrar definitivamente.
- El público solo ve los comentarios visibles.
- Botones de acción implementados con formularios **POST + CSRF** para seguridad.

### ⭐ Reviews
- Valoraciones de 1 a 5 estrellas.
- Promedio de reviews visible en cada post.
- Validación para evitar votos duplicados.

### 🎭 Reacciones rápidas (emoticones)
- Like 👍, Love ❤️, Risa 😂, Sorpresa 😮, Triste 😢.
- Un usuario puede reaccionar una sola vez por tipo en cada post.
- Toggle automático (añadir/quitar).
- Actualización en vivo con AJAX/HTMX.

### ⬆⬇ Votos y comentarios destacados
- Sistema de upvotes/downvotes en comentarios.
- Prevención de votos múltiples por usuario.
- Orden dinámico: **comentarios fijados → score → fecha**.
- Moderadores pueden fijar/desfijar comentarios.

### 📢 Menciones y notificaciones
- Detección automática de menciones (@usuario).
- Notificación al usuario mencionado con enlace directo al comentario.
- Bandeja de notificaciones con estado leído/no leído.

### 📰 Suscripciones y feeds
- Los usuarios pueden suscribirse a:
  - Autores específicos.
  - Etiquetas/temas.
- Feeds RSS generados automáticamente.
- Evita duplicados en suscripciones.

### 🔍 Extras
- Búsqueda de posts por título o contenido.
- Filtro por etiquetas.
- Paginación en listados.
- Panel de administración de Django para gestión global.

---

## 📦 Requisitos

Antes de comenzar, asegúrate de tener instalado:

- **Anaconda (conda 24+)**
- **Python 3.10+**
- **pip** (gestor de paquetes de Python)
- **SQLite** (incluido por defecto con Django)

Dependencias principales (archivo `requirements.txt`):
- Django
- Pillow (manejo de imágenes)
- django-ckeditor (texto enriquecido)
- django-taggit (etiquetas)
- crispy-forms (formularios estilizados)
- bootstrap (frontend)
- htmx (actualización parcial de vistas)

---

## ⚙ Instalación (con Anaconda)

```bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/Los5Furiosos/blog.git
cd blog

# 2️⃣ Crear entorno con Anaconda
conda create -n bloggame python=3.10 -y

# 3️⃣ Activar entorno
conda activate bloggame

# 4️⃣ Instalar dependencias
pip install -r requirements.txt

# 5️⃣ Aplicar migraciones
python manage.py migrate

# 6️⃣ Crear superusuario (para panel de administración)
python manage.py createsuperuser

# 7️⃣ Ejecutar servidor
python manage.py runserver

👉 Accede en tu navegador a: http://127.0.0.1:8000/


🛡 Moderación de comentarios

El dueño del post puede:

Bloquear (block) → marca el comentario como inapropiado.

Ocultar (hide) → lo quita de la vista pública.

Mostrar (show) → vuelve a hacerlo visible.

Eliminar (delete) → lo borra permanentemente.

La moderación se realiza directamente desde la vista del post.
Se usan formularios con POST y CSRF para máxima seguridad.


📂 Estructura del proyecto


blog/
├── blog/                # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/           # HTML templates
├── static/              # Archivos estáticos (CSS, JS, imágenes)
├── posts/               # App principal
│   ├── models.py        # Modelos: Post, Comment, Review, Reaction, Vote, Subscription, Notification
│   ├── views.py         # Lógica de negocio
│   ├── urls.py
│   ├── forms.py
│   └── templates/posts/
├── manage.py
└── requirements.txt



🛠️ Flujo de desarrollo (GitKraken)

Se trabaja con ramas feature/<nombre> para cada funcionalidad.

Pull requests hacia develop, no directamente a main.

Tablero Kanban: Backlog → In Progress → In Review → Done.

Cada PR debe incluir:

Descripción clara de cambios.

Checklist de pruebas.

Capturas de pantalla si aplica.

Pasos para reproducir.




🛡️ Seguridad básica

Uso de csrf_token en formularios.

Validación de datos de usuario en modelos y formularios.

Restricción de acciones sensibles a usuarios autenticados.

Control de permisos en comentarios y notificaciones.

Manejo de errores con códigos HTTP apropiados (403, 404, 429).




👥 Autores

Este proyecto fue desarrollado por el equipo Los5Furiosos:

Carlos Miranda

Eddie Man

Eliecias Cubilla

Harold Morales

Brayan Quintero





📜 Licencia

Este proyecto es de uso educativo y académico.
Puedes reutilizarlo y adaptarlo libremente siempre que cites a los autores originales.




---

👉 Ya lo puedes copiar tal cual como `README.md` en tu repo.  
¿Quieres que también te genere un **`requirements.txt` base** listo para este proyecto con Django + librerías (ckeditor, taggit, crispy, htmx, etc.) para que lo pegues directo en tu entorno `bloggame`?
