from django.urls import path, include

from apps.pockets.routers import pockets_router
from apps.targets.routers import target_router

urlpatterns = [
    path('auth/', include('apps.users.urls.auth')),
    path('users/', include('apps.users.urls.users_urls')),
    path('pockets/', include(pockets_router.urls)),
    path('targets/', include(target_router.urls)),
]
