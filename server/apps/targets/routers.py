from rest_framework.routers import DefaultRouter

from .viewsets.target import TargetViewSet

target_router = DefaultRouter()

target_router.register(
    prefix='targets',
    viewset=TargetViewSet,
    basename='targets'
)
