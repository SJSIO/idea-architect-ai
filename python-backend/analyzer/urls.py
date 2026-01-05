from django.urls import path

from .auth_views import RegisterView, LoginView, CurrentUserView
from .project_views import ProjectListCreateView, ProjectDetailView
from .views import (
    AnalyzeView, 
    health_check, 
    api_root,
    knowledge_status,
    knowledge_locations,
    refresh_knowledge,
    api_key_status,
)

urlpatterns = [
    # Root and health
    path('', api_root, name='api-root'),
    path('health', health_check, name='health-check'),
    
    # Authentication (MongoDB + JWT)
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/me', CurrentUserView.as_view(), name='current-user'),
    
    # Projects (MongoDB)
    path('projects', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<str:project_id>', ProjectDetailView.as_view(), name='project-detail'),
    
    # Analysis (LangGraph workflow)
    path('analyze', AnalyzeView.as_view(), name='analyze'),
    
    # Knowledge base management
    path('knowledge/status', knowledge_status, name='knowledge-status'),
    path('knowledge/locations', knowledge_locations, name='knowledge-locations'),
    path('knowledge/refresh', refresh_knowledge, name='knowledge-refresh'),
    
    # API key management
    path('api-keys/status', api_key_status, name='api-keys-status'),
]
