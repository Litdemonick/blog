# 📰 Blog Django – Autenticación, Autorización y Contenido Enriquecido

Proyecto académico y profesional desarrollado en *Django* que implementa un sistema de blog completo con autenticación de usuarios, autorización por roles, CRUD de publicaciones, comentarios con moderación, sistema de reviews y enriquecimiento de contenido.  
Este proyecto fue desarrollado por el equipo *Los5Furiosos*:  
*Carlos Miranda, Eddie Man, Eliecias Cubilla, Harold Morales y Brayan Quintero.*

---

## 🚀 Características principales

- 🔑 *Autenticación y autorización*
  - Registro y login con correo/usuario y contraseña.
  - Logout seguro (requiere POST por defecto).
  - Redirección tras crear cuenta o cerrar sesión.
  - Perfiles de usuario con avatar y bio.

- 📝 *Gestión de publicaciones (CRUD)*
  - Crear, leer, editar y eliminar posts.
  - Solo el autor puede editar o eliminar su propio contenido.
  - Integración con *ckeditor* para texto enriquecido.
  - Subida de imágenes mediante ImageField.
  - Etiquetas y categorías con *django-taggit*.
  - Paginación y búsqueda integrada.

- 💬 *Comentarios*
  - Los usuarios pueden comentar en los posts.
  - Los autores tienen control total sobre los comentarios de su post:
    - 🔒 Bloquear comentarios negativos.
    - 👁 Ocultar comentarios temporalmente.
    - 👁‍🗨 Mostrar comentarios ocultos.
    - 🗑 Eliminar comentarios.
  - El público solo ve comentarios con estado *Visible*.
  - Los dueños del post ven todos y tienen botones de moderación.

- ⭐ *Reviews*
  - Sistema de valoraciones de 1 a 5 estrellas.
  - Validación para evitar votos duplicados.
  - Promedio visible en el detalle de cada post.

- 🔍 *Extras*
  - Búsqueda de posts por título o contenido.
  - Filtro por etiquetas.
  - Paginación en listados.
  - Panel de administración de Django habilitado para control global.

---

## 📦 Requisitos

Antes de comenzar, asegúrate de tener instalado:

- *Python 3.10+*
- *pip* (gestor de paquetes de Python)
- *virtualenv* (opcional, pero recomendado)
- *SQLite* (incluido por defecto con Django)

Dependencias principales (en requirements.txt):
- Django
- Pillow (manejo de imágenes)
- django-ckeditor (texto enriquecido)
- django-taggit (etiquetas)
- crispy-forms (estilos de formularios)
- bootstrap (integración visual)

---

## ⚙ Instalación

Sigue estos pasos para clonar y ejecutar el proyecto en tu entorno local:

bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/Los5Furiosos/blog.git
cd blog

# 2️⃣ Crear un entorno virtual
python -m venv .venv

# 3️⃣ Activar el entorno virtual
# Linux/MacOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\activate

# 4️⃣ Instalar dependencias
pip install -r requirements.txt

# 5️⃣ Aplicar migraciones
python manage.py migrate

# 6️⃣ Crear superusuario (para acceso al panel de administración)
python manage.py createsuperuser

# 7️⃣ Ejecutar el servidor
python manage.py runserver


Accede en tu navegador a: 👉 http://127.0.0.1:8000/

---

## 🛡 Moderación de comentarios

El *dueño del post* puede:
- Bloquear (block) → marca el comentario como inapropiado.
- Ocultar (hide) → lo quita de la vista pública sin eliminarlo.
- Mostrar (show) → lo vuelve visible al público.
- Eliminar (delete) → lo borra permanentemente.

El control se hace directamente desde la vista de detalle del post.  
Se añadieron *botones con formularios POST y CSRF* para garantizar seguridad.

---

## 📂 Estructura del proyecto

bash
blog/
├── blog/                # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/           # Templates HTML (login, signup, base, posts)
├── static/              # Archivos estáticos (css, js, imágenes)
├── posts/               # App principal de posts
│   ├── models.py        # Modelos: Post, Comment, Review
│   ├── views.py         # Lógica de negocio
│   ├── urls.py
│   ├── forms.py
│   └── templates/posts/
├── manage.py
└── requirements.txt


---

## 👥 Autores

Este proyecto fue desarrollado por el equipo *Los5Furiosos*:

- *Carlos Miranda*  
- *Eddie Man*  
- *Eliecias Cubilla*  
- *Harold Morales*  
- *Brayan Quintero*

---

## 📜 Licencia

Este proyecto es de uso educativo y académico.  
Puedes reutilizarlo y adaptarlo libremente siempre que cites a los autores originales.

---