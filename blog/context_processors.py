from taggit.models import Tag

def global_tags(request):
    """
    Devuelve los tags para usarlos en todas las plantillas.
    """
    return {"all_tags": Tag.objects.all()[:15]}  # mostramos solo 15
