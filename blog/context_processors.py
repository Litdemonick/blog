from blog.models import Notification
from taggit.models import Tag

def unread_notifications(request):
    """Agrega el contador de notificaciones no leídas al contexto global"""
    if request.user.is_authenticated:
        return {
            "unread_count": request.user.notifications.filter(is_read=False).count()
        }
    return {"unread_count": 0}


def global_tags(request):
    """Devuelve los tags para usarlos en todas las plantillas"""
    return {"all_tags": Tag.objects.all()[:15]}  # mostramos solo 15
