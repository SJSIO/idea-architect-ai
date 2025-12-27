from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, AnalyzeView, health_check, api_root

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health', health_check, name='health-check'),
    path('analyze', AnalyzeView.as_view(), name='analyze'),
    path('', include(router.urls)),
]
