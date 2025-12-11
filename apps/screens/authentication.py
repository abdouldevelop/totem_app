from rest_framework import authentication
from rest_framework import exceptions
from .models import Screen


class ScreenTokenAuthentication(authentication.BaseAuthentication):
    """
    Authentication personnalisée pour les écrans utilisant un token dans le header
    """
    
    def authenticate(self, request):
        token = request.META.get('HTTP_X_SCREEN_TOKEN')
        
        if not token:
            return None
        
        try:
            screen = Screen.objects.get(api_token=token)
        except Screen.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token invalide')
        
        # On retourne un tuple (user, auth) mais pour les écrans on peut retourner (screen, token)
        # On crée un objet "user" factice pour que DRF soit content
        class ScreenUser:
            is_authenticated = True
            is_active = True
            
        return (ScreenUser(), screen)
