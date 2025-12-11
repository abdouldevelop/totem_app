# Templates HTML - Digital Signage

Ce dossier contient tous les templates HTML modernes créés avec **Tailwind CSS** pour l'interface web du système Digital Signage.

## 📁 Structure des Templates

```
backend/templates/
├── base.html                    # Template de base (layout principal)
├── dashboard.html               # Page d'accueil / tableau de bord
├── login.html                   # Page de connexion
├── screens/
│   ├── list.html               # Liste des écrans
│   └── detail.html             # Détails d'un écran
├── content/
│   └── list.html               # Bibliothèque de contenus
└── playlists/
    └── list.html               # Liste des playlists
```

## 🎨 Technologies Utilisées

- **Tailwind CSS 3.x** : Framework CSS moderne via CDN
- **Alpine.js** : Framework JavaScript léger pour l'interactivité
- **Chart.js** : Bibliothèque pour les graphiques
- **SVG Icons** : Icônes modernes intégrées

## 📄 Description des Templates

### 1. base.html
**Template principal** qui contient :
- Sidebar de navigation avec menu
- Header avec barre de recherche et profil utilisateur
- Zone de contenu principale
- Système de messages/alertes
- Design responsive (mobile-first)

**Blocs disponibles :**
```django
{% block title %}{% endblock %}
{% block page_title %}{% endblock %}
{% block page_subtitle %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_css %}{% endblock %}
{% block extra_js %}{% endblock %}
```

### 2. dashboard.html
**Tableau de bord principal** avec :
- 4 cartes de statistiques (écrans, contenus, playlists, vues)
- Graphique d'activité des 7 derniers jours
- État des écrans en temps réel
- Contenus récents
- Actions rapides

### 3. login.html
**Page de connexion** avec :
- Design moderne avec fond dégradé animé
- Formulaire de connexion sécurisé
- Option "Se souvenir de moi"
- Lien vers l'administration Django
- Design totalement responsive

### 4. screens/list.html
**Gestion des écrans** avec :
- Vue en grille des écrans
- Recherche et filtres
- Statut en temps réel (en ligne/hors ligne)
- Indicateurs d'activité
- Actions rapides (détails, logs)

### 5. screens/detail.html
**Détails d'un écran** avec :
- Informations complètes de l'écran
- Playlist actuelle assignée
- Logs d'activité récents
- Statistiques (vues, temps actif, heartbeats)
- Actions rapides (redémarrer, télécharger logs, etc.)

### 6. content/list.html
**Bibliothèque de contenus** avec :
- Vue en grille avec aperçus
- Filtres par type (image, vidéo, web)
- Recherche avancée
- Badges de type et durée
- Actions sur les contenus

### 7. playlists/list.html
**Gestion des playlists** avec :
- Cartes colorées pour chaque playlist
- Informations de planification
- Aperçu des contenus
- Statistiques rapides
- État actif/inactif

## 🚀 Intégration avec Django

### Configuration requise dans settings.py

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← Important !
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### Exemple de vue Django

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.screens.models import Screen
from apps.content.models import Content
from apps.playlists.models import Playlist

@login_required
def dashboard(request):
    context = {
        'stats': {
            'total_screens': Screen.objects.count(),
            'online_screens': Screen.objects.filter(is_online=True).count(),
            'total_content': Content.objects.count(),
            'active_content': Content.objects.filter(is_active=True).count(),
            'total_playlists': Playlist.objects.count(),
            'active_playlists': Playlist.objects.filter(is_active=True).count(),
            'views_today': 1234,  # Remplacer par vraie logique
        },
        'recent_screens': Screen.objects.all()[:5],
        'recent_content': Content.objects.all()[:5],
    }
    return render(request, 'dashboard.html', context)

@login_required
def screens_list(request):
    screens = Screen.objects.all()
    return render(request, 'screens/list.html', {'screens': screens})

@login_required
def content_list(request):
    contents = Content.objects.all()
    return render(request, 'content/list.html', {'contents': contents})

@login_required
def playlists_list(request):
    playlists = Playlist.objects.all()
    context = {
        'playlists': playlists,
        'active_playlists_count': playlists.filter(is_active=True).count(),
        'scheduled_playlists_count': playlists.filter(schedule_start_date__isnull=False).count(),
        'total_contents_count': Content.objects.count(),
        'assigned_screens_count': Screen.objects.filter(current_playlist__isnull=False).count(),
    }
    return render(request, 'playlists/list.html', context)
```

### Configuration des URLs

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from apps.screens import views as screen_views
from apps.content import views as content_views
from apps.playlists import views as playlist_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('', dashboard_view, name='dashboard'),

    # Screens
    path('screens/', screen_views.screens_list, name='screens_list'),
    path('screens/<int:pk>/', screen_views.screen_detail, name='screen_detail'),

    # Content
    path('content/', content_views.content_list, name='content_list'),
    path('content/create/', content_views.content_create, name='content_create'),
    path('content/<int:pk>/', content_views.content_detail, name='content_detail'),

    # Playlists
    path('playlists/', playlist_views.playlists_list, name='playlists_list'),
    path('playlists/create/', playlist_views.playlist_create, name='playlist_create'),
    path('playlists/<int:pk>/', playlist_views.playlist_detail, name='playlist_detail'),

    # Analytics
    path('analytics/', analytics_view, name='analytics'),
]
```

## 🎨 Personnalisation

### Couleurs du thème
Les couleurs peuvent être modifiées dans la configuration Tailwind dans `base.html` :

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',
                    500: '#3b82f6',  // Bleu principal
                    600: '#2563eb',
                    // ... autres nuances
                }
            }
        }
    }
}
```

### Sidebar
Pour ajouter des liens dans la sidebar, modifiez `base.html` section `<nav>` :

```html
<a href="{% url 'mon_url' %}"
   class="flex items-center px-4 py-3 text-gray-300 rounded-lg hover:bg-gray-700">
    <svg class="w-5 h-5 mr-3"><!-- Votre icône --></svg>
    Mon Lien
</a>
```

## 📱 Responsive Design

Tous les templates sont **entièrement responsive** avec :
- **Mobile** : Menu hamburger, colonnes empilées
- **Tablet** : Grille à 2 colonnes
- **Desktop** : Grille complète, sidebar fixe

### Points de rupture Tailwind :
- `sm:` 640px
- `md:` 768px
- `lg:` 1024px
- `xl:` 1280px

## ✨ Fonctionnalités Interactives

### Alpine.js
Gestion des états locaux :
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Contenu</div>
</div>
```

### Auto-hide des alertes
Les messages disparaissent automatiquement après 5 secondes.

### Animations
- Transitions CSS sur hover
- Animations de slide-in
- Pulse pour les statuts en ligne

## 🔒 Sécurité

Tous les templates utilisent :
- `{% csrf_token %}` dans les formulaires
- `@login_required` dans les vues
- Validation côté serveur

## 📦 Dépendances CDN

Les templates chargent automatiquement :
- Tailwind CSS 3.x
- Alpine.js 3.x
- Chart.js 4.x

**Note** : Pour la production, il est recommandé de :
1. Compiler Tailwind localement
2. Minifier les assets
3. Utiliser un CDN ou servir les fichiers localement

## 🚧 TODO / Améliorations futures

- [ ] Créer les templates manquants (formulaires, etc.)
- [ ] Ajouter pagination côté serveur
- [ ] Implémenter la recherche en temps réel
- [ ] Ajouter des graphiques supplémentaires
- [ ] Mode sombre (dark mode)
- [ ] Export PDF des rapports
- [ ] Notifications en temps réel (WebSocket)

## 📝 Notes de développement

- Les templates utilisent le système de blocks Django pour l'héritage
- Les URLs doivent être définies dans `urls.py` avec les noms correspondants
- Les modèles doivent avoir les méthodes et propriétés référencées (ex: `is_online`, `get_content_type_display`)
- Les images doivent être servies via `MEDIA_URL`

## 🆘 Support

Pour toute question ou problème :
1. Vérifiez que les URLs sont correctement configurées
2. Vérifiez que les vues retournent le bon contexte
3. Consultez la console du navigateur pour les erreurs JavaScript
4. Vérifiez les logs Django pour les erreurs de template

---

**Créé le** : 9 Décembre 2024
**Framework** : Django + Tailwind CSS
**Projet** : Digital Signage - ANStat
