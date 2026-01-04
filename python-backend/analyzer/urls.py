from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet, 
    AnalyzeView, 
    health_check, 
    api_root,
    knowledge_status,
    knowledge_locations,
    refresh_knowledge,
    api_key_status,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health', health_check, name='health-check'),
    path('analyze', AnalyzeView.as_view(), name='analyze'),
    # Knowledge base management
    path('knowledge/status', knowledge_status, name='knowledge-status'),
    path('knowledge/locations', knowledge_locations, name='knowledge-locations'),
    path('knowledge/refresh', refresh_knowledge, name='knowledge-refresh'),
    # API key management
    path('api-keys/status', api_key_status, name='api-keys-status'),
    path('', include(router.urls)),
]
