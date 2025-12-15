from django import template
from django.template.defaultfilters import filesizeformat

register = template.Library()


@register.filter
def safe_filesize(file_field):
    """
    Retourne la taille du fichier de manière sécurisée.
    Gère les erreurs d'encodage et les fichiers manquants.
    """
    try:
        if file_field and hasattr(file_field, 'size'):
            return filesizeformat(file_field.size)
    except (OSError, UnicodeEncodeError, UnicodeDecodeError, FileNotFoundError):
        pass
    return "N/A"
