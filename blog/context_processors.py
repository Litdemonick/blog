from blog.models import Notification
from taggit.models import Tag


def unread_notifications(request):
    """Agrega contador y lista de notificaciones al contexto global"""
    if request.user.is_authenticated:
        return {
            "unread_count": request.user.notifications.filter(is_read=False).count(),
            "notifications": request.user.notifications.all().order_by("-created_at")[:8],
        }
    return {"unread_count": 0, "notifications": []}



def global_tags(request):
    """Devuelve los tags para usarlos en todas las plantillas"""
    return {"all_tags": Tag.objects.all()[:15]}


def latest_notifications(request):
    """Devuelve las últimas notificaciones para el dropdown de la campanita"""
    if request.user.is_authenticated:
        return {
            "notifications": request.user.notifications.all().order_by("-created_at")[:8]
        }
    return {"notifications": []}
