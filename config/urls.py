from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

# API ViewSets
from apps.screens.views import ScreenViewSet
from apps.content.views import ContentViewSet
from apps.playlists.views import PlaylistViewSet

# Web Views
from apps.core import views as core_views
from apps.screens import views as screens_views
from apps.content import views as content_views
from apps.playlists import views as playlists_views

# Configuration du router pour l'API REST
router = DefaultRouter()
router.register(r'screens', ScreenViewSet, basename='screen')
router.register(r'content', ContentViewSet, basename='content')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    # =========================================================================
    # ADMINISTRATION DJANGO
    # =========================================================================
    path('admin/', admin.site.urls),

    # =========================================================================
    # API REST (pour l'application mobile)
    # =========================================================================
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # =========================================================================
    # AUTHENTIFICATION WEB
    # =========================================================================
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # =========================================================================
    # INTERFACE WEB - DASHBOARD
    # =========================================================================
    path('', core_views.dashboard, name='dashboard'),
    path('analytics/', core_views.analytics, name='analytics'),

    # =========================================================================
    # INTERFACE WEB - ÉCRANS
    # =========================================================================
    path('screens/', screens_views.screens_list, name='screens_list'),
    path('screens/create/', screens_views.screen_create, name='screen_create'),
    path('screens/<uuid:pk>/', screens_views.screen_detail, name='screen_detail'),
    path('screens/<uuid:pk>/edit/', screens_views.screen_edit, name='screen_edit'),
    path('screens/<uuid:pk>/assign-playlist/', screens_views.screen_assign_playlist, name='screen_assign_playlist'),
    path('screens/<uuid:pk>/restart/', screens_views.screen_restart, name='screen_restart'),
    path('screens/<uuid:pk>/logs/', screens_views.screen_logs, name='screen_logs'),
    path('screens/<uuid:pk>/logs/download/', screens_views.screen_download_logs, name='screen_download_logs'),
    path('screens/<uuid:pk>/configuration/', screens_views.screen_configuration, name='screen_configuration'),
    path('screens/<uuid:pk>/delete/', screens_views.screen_delete, name='screen_delete'),

    # =========================================================================
    # INTERFACE WEB - CONTENUS
    # =========================================================================
    path('content/', content_views.content_list, name='content_list'),
    path('content/create/', content_views.content_create, name='content_create'),
    path('content/<uuid:pk>/', content_views.content_detail, name='content_detail'),
    path('content/<uuid:pk>/edit/', content_views.content_edit, name='content_edit'),
    path('content/<uuid:pk>/delete/', content_views.content_delete, name='content_delete'),

    # =========================================================================
    # INTERFACE WEB - PLAYLISTS
    # =========================================================================
    path('playlists/', playlists_views.playlists_list, name='playlists_list'),
    path('playlists/create/', playlists_views.playlist_create, name='playlist_create'),
    path('playlists/<uuid:pk>/', playlists_views.playlist_detail, name='playlist_detail'),
    path('playlists/<uuid:pk>/edit/', playlists_views.playlist_edit, name='playlist_edit'),
    path('playlists/<uuid:pk>/delete/', playlists_views.playlist_delete, name='playlist_delete'),
]

# Servir les fichiers médias et statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration de l'admin Django
admin.site.site_header = "Digital Signage Manager"
admin.site.site_title = "Digital Signage"
admin.site.index_title = "Administration"
