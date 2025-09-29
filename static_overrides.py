from django.contrib.staticfiles.storage import StaticFilesStorage

class NoHashStaticFilesStorage(StaticFilesStorage):
    """
    Custom storage backend que desactiva los hashes en los archivos estáticos.
    Sirve los archivos tal cual están en /static/.
    """
    pass
