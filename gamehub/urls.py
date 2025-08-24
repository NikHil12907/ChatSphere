from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from games.views import GameViewSet, CategoryViewSet
from reviews.views import ReviewViewSet
from achievements.views import AchievementViewSet, UserAchievementViewSet
from social.views import FriendshipViewSet, GameSessionViewSet

# API Router
router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'achievements', AchievementViewSet)
router.register(r'user-achievements', UserAchievementViewSet)
router.register(r'friendships', FriendshipViewSet)
router.register(r'game-sessions', GameSessionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/auth/social/', include('allauth.socialaccount.urls')),
    
    # Custom app endpoints
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/games/', include('games.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/social/', include('social.urls')),
    
    # API documentation
    path('api/v1/docs/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)